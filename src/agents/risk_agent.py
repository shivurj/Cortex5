from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.state import AgentState

class RiskAgent(BaseAgent):
    def __init__(self, model):
        super().__init__(
            name="RiskAgent",
            model=model,
            tools=[]
        )
        self.system_prompt = "You are the Risk Manager. You are the gatekeeper. You review the `trade_signal`. If the signal is BUY, check if we have enough capital. If the volatility is too high, set `risk_approval` to False. You are conservative and paranoid."

    def run(self, state: AgentState) -> Dict[str, Any]:
        # Logic to update risk_approval in state
        # Rule: Reject any trade if sentiment_score < 0.5 for a BUY signal
        return super().run(state)
