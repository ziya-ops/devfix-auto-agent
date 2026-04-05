from langgraph.graph import StateGraph, START, END
from state import AgentState
from nodes import planner_node, coder_node, validator_node, executor_node, reflector_node

def should_continue(state: AgentState):
    if state.get("attempts", 0) >= 5:
        return "end"
    if state.get("error") or "failed" in state.get("test_results", ""):
        return "reflect"
    return "end"

def validator_routing(state: AgentState):
    # First check if we should continue
    if state.get("attempts", 0) >= 5:
        return "end"
    if state.get("error"):
        return "reflect"
    # If we have test results and they pass, we're done
    if state.get("test_results") and "passed" in state["test_results"] and "failed" not in state["test_results"]:
        return "end"
    # If no error but no successful test results, execute tests
    if not state.get("test_results"):
        return "executor"
    # If tests failed, reflect and try again
    return "reflect"

graph_builder = StateGraph(AgentState)
graph_builder.add_node("planner", planner_node)
graph_builder.add_node("coder", coder_node)
graph_builder.add_node("validator", validator_node)
graph_builder.add_node("executor", executor_node)
graph_builder.add_node("reflector", reflector_node)

graph_builder.set_entry_point("planner")
graph_builder.add_edge("planner", "coder")
graph_builder.add_edge("coder", "validator")
graph_builder.add_conditional_edges(
    "validator",
    validator_routing,
    {"executor": "executor", "reflector": "reflector", "end": END}
)
graph_builder.add_edge("executor", "validator")
graph_builder.add_edge("reflector", "coder")

devfix_graph = graph_builder.compile()