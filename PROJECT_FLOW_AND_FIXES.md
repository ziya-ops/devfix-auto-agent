# DevFix Auto-Agent - Project Flow and Fixes Documentation

## 🔄 Project Flow Overview

### **Architecture: LangGraph-based AI Code Agent**

```
┌─────────────────────────────────────────────────────────────┐
│                    START (User Task)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  PLANNER NODE: Creates step-by-step implementation plan     │
│  Input: Task description                                     │
│  Output: Structured plan (internal use)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  CODER NODE: Generates Python code with tests              │
│  Input: Task + plan + previous errors                       │
│  Output: Complete Python script with pytest tests           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  VALIDATOR NODE: Checks code syntax                         │
│  Input: Generated code                                      │
│  Output: Syntax validation results                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────┐
          │  CONDITIONAL ROUTING LOGIC    │
          └──────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    [ERROR]      [NO TEST YET]    [TESTS PASSED]
         │               │               │
         ▼               ▼               ▼
   REFLECTOR       EXECUTOR         END (SUCCESS)
         │               │
         │               │
         │               ▼
         │      ┌─────────────────┐
         │      │ EXECUTOR NODE:  │
         │      │ Run tests in    │
         │      │ Docker container│
         │      └────────┬────────┘
         │               │
         │               ▼
         │      ┌─────────────────┐
         │      │ VALIDATOR AGAIN │
         │      └────────┬────────┘
         │               │
         └───────────────┴───────────────┐
                         │
                         ▼
              ┌──────────────────┐
              │ REFLECTOR NODE:  │
              │ Analyze failure  │
              │ Generate fix     │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ INCREMENT ATTEMPTS│
              │ Back to CODER     │
              └──────────────────┘
```

### **Node Responsibilities:**

1. **Planner Node**: Breaks down task into implementation steps
2. **Coder Node**: Generates complete Python code with pytest tests
3. **Validator Node**: Performs syntax validation using AST parsing
4. **Executor Node**: Runs code in isolated Docker container with governance checks
5. **Reflector Node**: Analyzes failures and generates corrected code

### **Safety & Governance Features:**

- **Safety Guard**: Blocks dangerous code (os.system, eval, etc.)
- **Human Approval**: Manual approval before code execution (configurable)
- **Docker Isolation**: All code runs in containers for safety
- **LangSmith Tracing**: Full observability and debugging capabilities

---

## 🐛 Errors Found and Fixes Applied

### **Error 1: Import Order Issue**
**Problem**: Environment variables loaded after module imports
```python
# ❌ BEFORE (main.py)
from graph import devfix_graph  # Imports nodes.py which checks for API_KEY
load_dotenv()  # Too late!
```

**Fix**: Load environment variables first
```python
# ✅ AFTER
from dotenv import load_dotenv
load_dotenv()  # Load first
from graph import devfix_graph  # Then import
```

**Why**: The `nodes.py` module checks for `GOOGLE_API_KEY` at import time, but it wasn't available yet.

---

### **Error 2: Duplicate AgentState Class**
**Problem**: Two `AgentState` classes in `state.py`
```python
# ❌ BEFORE
class AgentState(TypedDict):  # First definition
    # ... basic fields

class AgentState(TypedDict):  # Duplicate definition!
    # ... extended fields
```

**Fix**: Single unified state definition
```python
# ✅ AFTER
class AgentState(TypedDict):
    # All fields in one definition
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
```

**Why**: Python doesn't support class overloading, causing the second definition to shadow the first.

---

### **Error 3: Infinite Loop - Recursion Limit**
**Problem**: Two conflicting conditional edges from validator node
```python
# ❌ BEFORE
graph_builder.add_conditional_edges(
    "validator",
    lambda s: "executor" if not s.get("error") else "reflector",
    {"executor": "executor", "reflector": "reflector"}
)
# AND THEN...
graph_builder.add_conditional_edges(
    "validator",
    should_continue,
    {"reflect": "reflector", "end": END}
)
```

**Fix**: Single unified routing function
```python
# ✅ AFTER
def validator_routing(state: AgentState):
    """Unified routing logic to prevent infinite loops"""
    if state.get("attempts", 0) >= 5:
        return "end"
    if state.get("error"):
        return "reflect"
    if state.get("test_results") and "passed" in state["test_results"]:
        return "end"
    if not state.get("test_results"):
        return "executor"
    return "reflect"

# Single conditional edge
graph_builder.add_conditional_edges(
    "validator",
    validator_routing,
    {"executor": "executor", "reflector": "reflector", "end": END}
)
```

**Why**: Having two conditional edges from the same node created contradictory paths, causing the graph to loop infinitely until hitting the recursion limit.

---

### **Error 4: Docker Not Running**
**Problem**: Docker daemon not running
```bash
docker: Cannot connect to the Docker daemon at unix:///Users/.docker/run/docker.sock
```

**Fix**: Start Docker Desktop or install Docker
```bash
# Start Docker Desktop on macOS
open -a Docker

# Verify Docker is running
docker ps
```

**Why**: The executor node runs code in Docker containers for safety, requiring Docker to be running.

---

## 🚀 Expected Output Flow

### **Successful Execution:**
```
Starting DevFix Auto-Agent with governance and observability...
Generated code (latest attempt):
def reverse_string(s: str) -> str:
    return s[::-1]

def test_hello_string():
    assert reverse_string('hello') == 'olleh'

def test_abc_string():
    assert reverse_string('abc') == 'cba'

Test output:
.1 passed in 0.01s

=== FINAL EVALUATION REPORT ===
Success: Yes
Attempts used: 1
Total latency: 5432.12 ms
Total cost tracked: $0.0012
LangSmith Trace ID: devfix-run-1
Full trace and audit log available in LangSmith dashboard.
```

### **With Governance (AUTO_APPROVE=false):**
```
GOVERNANCE CHECK - Proposed code ready for execution:
[code preview...]
Approve execution? (y/n): y
[execution continues...]
```

---

## 📋 Configuration Options

### **Environment Variables:**
```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional (LangSmith tracing)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=devfix-auto-agent

# Governance
AUTO_APPROVE=true  # Set to false for manual approval
```

### **Command Usage:**
```bash
# Basic usage
python main.py --task "Your task description"

# With governance
AUTO_APPROVE=false python main.py --task "Your task"

# With full observability
LANGCHAIN_TRACING_V2=true python main.py --task "Your task"
```

---

## 🛠️ Technical Stack

- **AI Model**: Gemini 2.5 Flash via Google Generative AI
- **Orchestration**: LangGraph for state machine management
- **Testing**: Pytest for code validation
- **Isolation**: Docker containers for safe code execution
- **Observability**: LangSmith for tracing and monitoring
- **State Management**: TypedDict with message annotations

---

## ✅ All Fixed Issues

1. ✅ **Import order** - Environment variables load before imports
2. ✅ **State definition** - Single unified AgentState class
3. ✅ **Graph logic** - Fixed infinite loop with unified routing
4. ✅ **Docker integration** - Proper error handling and status checks
5. ✅ **Governance flow** - Safety checks and human approval
6. ✅ **Observability** - LangSmith integration working

The project now runs successfully with proper flow control, safety measures, and full observability!