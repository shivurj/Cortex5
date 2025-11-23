from typing import Dict, Any
from langchain_core.tools import tool
from src.agents.base_agent import BaseAgent
from src.state import AgentState
import yfinance as yf

@tool
def fetch_stock_data(ticker: str) -> Dict[str, Any]:
    """Fetches raw OHLCV data from Yahoo Finance."""
    try:
        stock = yf.Ticker(ticker)
        # Get last 1 month of data
        hist = stock.history(period="1mo")
        return hist.to_dict()
    except Exception as e:
        return {"error": str(e)}

class DataAgent(BaseAgent):
    def __init__(self, model):
        super().__init__(
            name="DataAgent",
            model=model,
            tools=[fetch_stock_data]
        )
        self.system_prompt = "You are the Data Engineer. Your job is to fetch raw OHLCV data from Yahoo Finance and query TimescaleDB. You do not analyze, you only provide facts."

    def run(self, state: AgentState) -> Dict[str, Any]:
        # In a real implementation, the LLM would decide to call the tool.
        # Here we manually invoke the tool for demonstration if it's not already in market_data
        # Or we let the LLM do it.
        # For Day 1 simplicity, let's assume the LLM will call the tool.
        return super().run(state)
