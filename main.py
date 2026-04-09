import os
import time
import argparse

# Load environment variables FIRST before importing anything that needs them
from dotenv import load_dotenv
load_dotenv()

# Now import modules that depend on environment variables
from graph import devfix_graph
from state import AgentState
from observability import get_tracer, log_metric

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="Task description + test requirements")
    args = parser.parse_args()

    initial_state: AgentState = {
        "task": args.task,
        "messages": [],
        "code": "",
        "error": "",
        "test_results": "",
        "attempts": 0,
        "approved": False,
        "total_cost": 0.0,
        "latency_ms": 0.0,
        "audit_log": [],
        "run_id": None
    }

    tracer = get_tracer()
    config = {"configurable": {"thread_id": "devfix-run-1"}, "callbacks": [tracer]}

    print("Starting DevFix Auto-Agent with governance and observability...")

    start_time = time.time()
    for event in devfix_graph.stream(initial_state, config=config, stream_mode="values"):
        if "code" in event and event["code"]:
            print("Generated code (latest attempt):")
            print(event["code"][:500] + "..." if len(event["code"]) > 500 else event["code"])
        if "test_results" in event and event["test_results"]:
            print(f"Test output:\n{event['test_results']}\n")
        if "error" in event and event["error"]:
            print(f"Error: {event['error']}\n")
        if "run_id" not in event and "run_id" in config.get("configurable", {}):
            event["run_id"] = config["configurable"]["thread_id"]

    total_time = (time.time() - start_time) * 1000

    final_state = event
    final_state["latency_ms"] = total_time
    final_state["audit_log"].append({"step": "final", "timestamp": time.time(), "status": "success" if "passed" in final_state.get("test_results", "") else "failed"})

    print("\n=== FINAL EVALUATION REPORT ===")
    print(f"Success: {'Yes' if 'passed' in final_state.get('test_results', '') else 'No'}")
    print(f"Attempts used: {final_state.get('attempts', 0)}")
    print(f"Total latency: {final_state['latency_ms']:.2f} ms")
    print(f"Total cost tracked: ${final_state.get('total_cost', 0):.4f}")
    print(f"LangSmith Trace ID: {final_state.get('run_id')}")
    print("Full trace and audit log available in LangSmith dashboard.")

    if final_state.get("run_id"):
        log_metric(final_state["run_id"], "success", 1.0 if "passed" in final_state.get("test_results", "") else 0.0)
        log_metric(final_state["run_id"], "attempts", final_state.get("attempts", 0))