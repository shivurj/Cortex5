import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from src.graph import create_graph

# Load environment variables
load_dotenv()

def main():
    print("Initializing Cortex5 AI Hedge Fund...")
    
    # Create the graph
    app = create_graph()
    
    # Define initial state
    initial_state = {
        "messages": [HumanMessage(content="Analyze AAPL and execute trade if favorable.")],
        "market_data": {},
        "sentiment_score": 0.0,
        "trade_signal": "HOLD",
        "risk_approval": False,
        "execution_status": "PENDING"
    }
    
    print("Starting execution flow...")
    # Run the graph
    for output in app.stream(initial_state):
        for key, value in output.items():
            print(f"Finished running: {key}")
            # print(f"Output: {value}") # Uncomment to see full state updates
            
    print("Execution complete.")

if __name__ == "__main__":
    main()
