from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    task: str
    code: str
    error: str
    test_results: str
    attempts: int
    approved: bool
    total_cost: float
    latency_ms: float
    audit_log: list
    run_id: Optional[str]