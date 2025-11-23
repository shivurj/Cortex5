from typing import Dict, Any
from langchain_core.tools import tool
from src.agents.base_agent import BaseAgent
from src.state import AgentState

@tool
def query_news_vectors(query: str) -> str:
    """Queries Qdrant vector DB to find similar historical news."""
    # Mock implementation for Day 1
    return "Positive sentiment detected in recent news regarding tech sector."

class SentimentAgent(BaseAgent):
    def __init__(self, model):
        super().__init__(
            name="SentimentAgent",
            model=model,
            tools=[query_news_vectors]
        )
        self.system_prompt = "You are the Sentiment Analyst. Your job is to read news headlines and output a sentiment score between 0 (Bearish) and 1 (Bullish). You use the Qdrant vector DB to find similar historical news."

    def run(self, state: AgentState) -> Dict[str, Any]:
        # Logic to update sentiment_score in state
        # For now, we just return the LLM response
        return super().run(state)
