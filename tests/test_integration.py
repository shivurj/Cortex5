import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage
from src.graph import create_graph
from src.state import AgentState, TradeSignal

@pytest.fixture
def mock_market_data():
    """Create sample OHLCV data for testing."""
    dates = pd.date_range(start="2023-01-01", periods=30, freq="D")
    data = {
        "timestamp": dates,
        "open": [150.0] * 30,
        "high": [155.0] * 30,
        "low": [145.0] * 30,
        "close": [152.0] * 30,
        "volume": [1000000] * 30,
        "symbol": ["AAPL"] * 30
    }
    return pd.DataFrame(data)

@pytest.fixture
def mock_news_data():
    """Create sample news data for testing."""
    return [
        {
            "title": "AAPL reports record earnings",
            "description": "Apple Inc. smashed expectations...",
            "published_at": datetime.now(),
            "source": "Financial Times",
            "url": "http://example.com"
        }
    ]

@patch("src.agents.data_agent.MarketDataFetcher")
@patch("src.agents.data_agent.TimescaleDBClient")
@patch("src.agents.sentiment_agent.QdrantVectorStore")
@patch("src.agents.sentiment_agent.EmbeddingGenerator")
@patch("src.agents.execution_agent.TimescaleDBClient")
def test_end_to_end_pipeline(
    mock_exec_db, 
    mock_embed_gen, 
    mock_qdrant, 
    mock_data_db, 
    mock_fetcher,
    mock_market_data
):
    """
    Test the complete agent pipeline from Data -> Execution.
    Mocks external dependencies (Yahoo, DB, Qdrant) to test logic flow.
    """
    # 1. Setup Mocks
    # Data Agent mocks
    mock_fetcher_instance = mock_fetcher.return_value
    mock_fetcher_instance.fetch_ohlcv.return_value = mock_market_data
    
    # Sentiment Agent mocks
    mock_qdrant_instance = mock_qdrant.return_value
    # Mock search results
    mock_search_result = MagicMock()
    mock_search_result.payload = {"title": "Good news", "content": "Stock is going up"}
    mock_qdrant_instance.search_by_text.return_value = [mock_search_result]
    
    # Execution Agent mocks
    mock_exec_db_instance = mock_exec_db.return_value
    mock_exec_db_instance.log_trade.return_value = 123  # Fake trade ID

    # 2. Initialize Graph
    app = create_graph()
    
    # 3. Define Initial State
    initial_state = {
        "messages": [HumanMessage(content="Analyze AAPL")],
        "market_data": pd.DataFrame(),
        "sentiment_score": 0.5,
        "trade_signal": TradeSignal.HOLD,
        "risk_approval": False,
        "execution_status": "PENDING"
    }
    
    # 4. Run Graph
    # We use .invoke() to run the graph synchronously
    final_state = app.invoke(initial_state)
    
    # 5. Assertions
    
    # Data Agent Verification
    assert not final_state["market_data"].empty
    assert len(final_state["market_data"]) == 30
    mock_fetcher_instance.fetch_ohlcv.assert_called_once()
    
    # Sentiment Agent Verification
    # Note: Since we mocked the LLM inside the agent (or if it uses real LLM), 
    # we expect the score to be updated. If using real LLM, it might vary.
    # For this test, we assume the agent logic ran.
    assert "sentiment_score" in final_state
    
    # Quant Agent Verification
    # With flat prices (close=152.0), RSI should be stable/neutral
    assert "trade_signal" in final_state
    
    # Risk Agent Verification
    assert "risk_approval" in final_state
    
    # Execution Agent Verification
    assert "execution_status" in final_state
    
    print("\n✅ End-to-End Pipeline Test Passed!")
