import os
import ast
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from docker_utils import execute_code_in_docker

# Get API key from environment
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set. Please set it in your .env file.")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, api_key=google_api_key)

def planner_node(state: dict):
    prompt = f"""You are a senior software architect. Break down this task into clear steps:
Task: {state['task']}
Provide a short numbered plan only."""
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"messages": [response]}

def coder_node(state: dict):
    prompt = f"""Task: {state['task']}
Previous error: {state.get('error', 'None')}
Test results: {state.get('test_results', 'None')}

Write ONLY a complete, self-contained Python script that:
- Defines the required function/class
- Includes pytest test functions (def test_...)
- Uses pytest conventions
- No extra text, no markdown, just valid Python code."""
    response = llm.invoke([HumanMessage(content=prompt)])
    code = response.content.strip()
    if code.startswith("```python"):
        code = code.split("```python")[1].split("```")[0].strip()
    return {"code": code, "messages": [response]}

def validator_node(state: dict):
    try:
        ast.parse(state["code"])
        return {"error": ""}
    except SyntaxError as e:
        return {"error": f"SyntaxError: {str(e)}"}

def executor_node(state: dict):
    success, output = execute_code_in_docker(state["code"])
    return {"test_results": output, "error": "" if success else output}

def reflector_node(state: dict):
    prompt = f"""Analyze why the code failed and provide a precise fix.
Task: {state['task']}
Current code:
{state['code']}
Error / Test output:
{state.get('error') or state.get('test_results')}
Return ONLY the corrected full Python script (same format as before)."""
    response = llm.invoke([HumanMessage(content=prompt)])
    code = response.content.strip()
    if code.startswith("```python"):
        code = code.split("```python")[1].split("```")[0].strip()
    return {"code": code, "messages": [response], "attempts": state.get("attempts", 0) + 1}