import time
from pydantic import BaseModel, Field
from typing import Literal

class SafetyCheck(BaseModel):
    is_safe: bool = Field(description="True if code is safe to execute")
    reason: str = Field(description="Short reason for decision")
    risk_level: Literal["low", "medium", "high"] = Field(description="Risk classification")

def safety_guard(code: str) -> SafetyCheck:
    # Simple rule-based + LLM guard (production version would use LlamaGuard or Bedrock Guardrails)
    dangerous_keywords = ["os.system", "subprocess", "eval(", "exec(", "open(", "rm -rf"]
    for kw in dangerous_keywords:
        if kw in code.lower():
            return SafetyCheck(is_safe=False, reason="Dangerous system command detected", risk_level="high")
    return SafetyCheck(is_safe=True, reason="Code passed basic safety checks", risk_level="low")

def human_approval(code: str, auto_approve: bool = False) -> bool:
    if auto_approve:
        return True
    print("GOVERNANCE CHECK - Proposed code ready for execution:")
    print(code[:800] + "..." if len(code) > 800 else code)
    response = input("Approve execution? (y/n): ").strip().lower()
    return response == "y"