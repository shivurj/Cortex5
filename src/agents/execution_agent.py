from typing import Dict, Any
from langchain_core.tools import tool
from src.agents.base_agent import BaseAgent
from src.state import AgentState

@tool
def execute_order(symbol: str, side: str, quantity: int) -> str:
    """Executes a trade order."""
    print(f"EXECUTING ORDER: {side} {quantity} {symbol}")
    return f"Executed {side} {quantity} {symbol}"

class ExecutionAgent(BaseAgent):
    def __init__(self, model):
        super().__init__(
            name="ExecutionAgent",
            model=model,
            tools=[execute_order]
        )
        self.system_prompt = "You are the Head Trader. You only execute if `risk_approval` is True. You log the trade details into the `execution_status` field."

    def run(self, state: AgentState) -> Dict[str, Any]:
        # Logic to update execution_status in state
        return super().run(state)
