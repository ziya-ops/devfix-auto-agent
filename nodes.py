import os
import ast
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from docker_utils import execute_code_in_docker
from governance import safety_guard, human_approval
from observability import log_metric

# Get API key from environment
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set. Please set it in your .env file.")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, api_key=google_api_key)

def planner_node(state: dict):
    prompt = f"You are a senior software architect. Break down this task into clear steps:\nTask: {state['task']}\nProvide a short numbered plan only."
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"messages": [response]}

def coder_node(state: dict):
    prompt = f"Task: {state['task']}\nPrevious error: {state.get('error', 'None')}\nTest results: {state.get('test_results', 'None')}\n\nWrite ONLY a complete, self-contained Python script that:\n- Defines the required function/class\n- Includes pytest test functions (def test_...)\n- Uses pytest conventions\n- No extra text, no markdown, just valid Python code."
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
    start_time = time.time()
    safety = safety_guard(state["code"])
    if not safety.is_safe:
        return {"error": f"SAFETY BLOCKED: {safety.reason}", "test_results": ""}
    approved = human_approval(state["code"], auto_approve=os.getenv("AUTO_APPROVE", "false").lower() == "true")
    if not approved:
        return {"error": "Execution rejected by human governance", "test_results": ""}
    success, output = execute_code_in_docker(state["code"])
    latency = (time.time() - start_time) * 1000
    return {"test_results": output, "error": "" if success else output, "latency_ms": latency}

def reflector_node(state: dict):
    prompt = f"Analyze why the code failed and provide a precise fix.\nTask: {state['task']}\nCurrent code:\n{state['code']}\nError / Test output:\n{state.get('error') or state.get('test_results')}\nReturn ONLY the corrected full Python script (same format as before)."
    response = llm.invoke([HumanMessage(content=prompt)])
    code = response.content.strip()
    if code.startswith("```python"):
        code = code.split("```python")[1].split("```")[0].strip()
    return {"code": code, "messages": [response], "attempts": state.get("attempts", 0) + 1}