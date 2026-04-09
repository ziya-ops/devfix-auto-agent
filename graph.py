import os
from langgraph.graph import StateGraph, START, END
from state import AgentState
from nodes import planner_node, coder_node, validator_node, executor_node, reflector_node
from observability import get_tracer

def validator_routing(state: AgentState):
    """
    Unified routing logic from validator to prevent infinite loops.
    Must return exact node names that match the conditional edges mapping.
    """
    # Check max attempts first
    if state.get("attempts", 0) >= 5:
        return "end"

    # If there's a syntax error, go to reflection
    if state.get("error"):
        return "reflector"  # Fixed: was "reflect", should be "reflector"

    # If we have successful test results, we're done
    if state.get("test_results") and "passed" in state["test_results"] and "failed" not in state["test_results"]:
        return "end"

    # If no test results yet, go to executor
    if not state.get("test_results"):
        return "executor"

    # If tests failed, go to reflection
    return "reflector"  # Fixed: was "reflect", should be "reflector"

graph_builder = StateGraph(AgentState)
graph_builder.add_node("planner", planner_node)
graph_builder.add_node("coder", coder_node)
graph_builder.add_node("validator", validator_node)
graph_builder.add_node("executor", executor_node)
graph_builder.add_node("reflector", reflector_node)

graph_builder.set_entry_point("planner")
graph_builder.add_edge("planner", "coder")
graph_builder.add_edge("coder", "validator")

# Single unified conditional edge from validator
graph_builder.add_conditional_edges(
    "validator",
    validator_routing,
    {
        "executor": "executor",
        "reflector": "reflector",
        "end": END
    }
)

graph_builder.add_edge("executor", "validator")
graph_builder.add_edge("reflector", "coder")

devfix_graph = graph_builder.compile(
    checkpointer=None,  # add PostgresSaver later for persistence
    interrupt_before=["executor"] if os.getenv("AUTO_APPROVE", "false").lower() != "true" else None
)