# Dev Fix Auto Agent

fully autonomous CLI-based coding agent that takes a single task fom you and then runs a closed loop cycle until the code works perfectly

1. planner
2. coder
3. validator (syntax)
4. executor (run it in docker)
5. reflector (check tests or errors)
6. repeats

features
- stateful
- cyclic
- self-correcting system

Tech Topics to build this solution
- stateful agentic loops (langgraph)
- reflexion pattern (self-healing architectures) - reflection or ReAct + Critique
- docker sandboxing
- AST (abstract syntax tree) parsing
- pytest for deterministic evaluation
- shared state management

- observability (langsmith)
- governance layer (safety guardrails, human in the loop)
- evaluation metrics
- audit logging and traceability