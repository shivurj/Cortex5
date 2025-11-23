from typing import List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from src.state import AgentState

# Import Agents
from src.agents.data_agent import DataAgent
from src.agents.sentiment_agent import SentimentAgent
from src.agents.quant_agent import QuantAgent
from src.agents.risk_agent import RiskAgent
from src.agents.execution_agent import ExecutionAgent

def create_graph():
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o")

    # Initialize Agents
    data_agent = DataAgent(llm)
    sentiment_agent = SentimentAgent(llm)
    quant_agent = QuantAgent(llm)
    risk_agent = RiskAgent(llm)
    execution_agent = ExecutionAgent(llm)

    # Define the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("DataAgent", data_agent.run)
    workflow.add_node("SentimentAgent", sentiment_agent.run)
    workflow.add_node("QuantAgent", quant_agent.run)
    workflow.add_node("RiskAgent", risk_agent.run)
    workflow.add_node("ExecutionAgent", execution_agent.run)

    # Define edges
    workflow.set_entry_point("DataAgent")
    workflow.add_edge("DataAgent", "SentimentAgent")
    workflow.add_edge("SentimentAgent", "QuantAgent")
    workflow.add_edge("QuantAgent", "RiskAgent")
    workflow.add_edge("RiskAgent", "ExecutionAgent")
    workflow.add_edge("ExecutionAgent", END)

    # Compile
    app = workflow.compile()
    return app
