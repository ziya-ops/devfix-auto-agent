from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    task: str
    code: str
    error: str
    test_results: str
    attempts: int