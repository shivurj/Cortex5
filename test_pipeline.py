#!/usr/bin/env python3
"""Quick test script to verify the agent pipeline works end-to-end."""

import asyncio
import sys
sys.path.insert(0, '/Volumes/Dhitva/Bots/Interview_Prep/Cortex5')

from src.graph import create_graph

def test_agent_pipeline():
    """Test the complete agent pipeline."""
    print("="*60)
    print("TESTING CORTEX5 AGENT PIPELINE")
    print("="*60)
    
    # Create a simple callback to print events
    def callback(payload):
        agent = payload.get('agent', 'Unknown')
        message = payload.get('message', '')
        msg_type = payload.get('type', 'info')
        print(f"[{agent}] [{msg_type.upper()}] {message}")
    
    # Create the graph with callback
    print("\n1. Creating agent graph...")
    graph = create_graph(callback=callback)
    print("✓ Graph created\n")
    
    # Initial state
    from langchain_core.messages import HumanMessage
    initial_state = {
        "messages": [HumanMessage(content="Analyze AAPL")],
        "data": {"ticker": "AAPL"}
    }
    
    print("2. Running agent pipeline for AAPL...\n")
    print("-"*60)
    
    # Run the graph
    result = graph.invoke(initial_state)
    
    print("-"*60)
    print("\n3. Pipeline complete!\n")
    
    # Print final results
    print("="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"Trade Signal: {result.get('trade_signal', 'N/A')}")
    print(f"Sentiment Score: {result.get('sentiment_score', 'N/A')}")
    print(f"Risk Approval: {result.get('risk_approval', 'N/A')}")
    print(f"Execution Status: {result.get('execution_status', 'N/A')}")
    print("="*60)
    
    return result

if __name__ == "__main__":
    result = test_agent_pipeline()
