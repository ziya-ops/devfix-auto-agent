import os
import warnings
import argparse

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Import after environment is loaded
from graph import devfix_graph
from state import AgentState

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
        "attempts": 0
    }

    print("Starting DevFix Auto-Agent...\n")
    for event in devfix_graph.stream(initial_state, stream_mode="values"):
        if "code" in event and event["code"]:
            print("Generated code (latest attempt):")
            print(event["code"][:500] + "..." if len(event["code"]) > 500 else event["code"])
        if "test_results" in event and event["test_results"]:
            print(f"Test output:\n{event['test_results']}\n")
        if "error" in event and event["error"]:
            print(f"Error: {event['error']}\n")

    final_state = event
    if final_state.get("test_results") and "passed" in final_state["test_results"]:
        print("SUCCESS! All tests passed.")
        print("\nFinal code:\n" + final_state["code"])
    else:
        print("Max attempts reached or tests still failing.")