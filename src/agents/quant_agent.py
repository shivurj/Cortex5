from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.state import AgentState

def calculate_rsi(prices, period=14):
    # Mock RSI calculation
    return 55.0

class QuantAgent(BaseAgent):
    def __init__(self, model):
        super().__init__(
            name="QuantAgent",
            model=model,
            tools=[]
        )
        self.system_prompt = "You are the Quant Researcher. You analyze the `market_data` provided by the Data Agent and the `sentiment_score` from the Sentiment Agent. You output a `trade_signal` (BUY/SELL/HOLD) based on technical indicators like RSI and MACD."

    def run(self, state: AgentState) -> Dict[str, Any]:
        # Logic to update trade_signal in state
        return super().run(state)
