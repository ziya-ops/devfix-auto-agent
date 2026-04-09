import os
from langsmith import Client
from langchain_core.tracers import LangChainTracer

client = Client()

def get_tracer():
    return LangChainTracer(
        project_name=os.getenv("LANGCHAIN_PROJECT"),
        client=client
    )

def log_metric(run_id, metric_name, value):
    client.create_feedback(
        run_id=run_id,
        key=metric_name,
        score=value
    )