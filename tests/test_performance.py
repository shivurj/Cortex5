import pytest
import time
import pandas as pd
from langchain_core.messages import HumanMessage
from src.data.market_fetcher import MarketDataFetcher
from src.data.embeddings import EmbeddingGenerator
from src.data.qdrant_client import QdrantVectorStore
from src.graph import create_graph
from src.state import TradeSignal

# Performance Thresholds (Seconds)
MAX_FETCH_TIME = 5.0
MAX_EMBEDDING_TIME = 2.0  # For a small batch
MAX_SEARCH_TIME = 1.0
MAX_GRAPH_EXECUTION_TIME = 15.0

@pytest.mark.benchmark
def test_market_data_fetch_performance():
    """Benchmark Yahoo Finance data fetching."""
    fetcher = MarketDataFetcher()
    start_time = time.perf_counter()
    df = fetcher.fetch_ohlcv("AAPL", period="1mo")
    duration = time.perf_counter() - start_time
    
    print(f"\n⏱️ Market Data Fetch: {duration:.4f}s")
    assert duration < MAX_FETCH_TIME
    assert not df.empty

@pytest.mark.benchmark
def test_embedding_generation_performance():
    """Benchmark embedding generation speed."""
    generator = EmbeddingGenerator()
    texts = ["Financial news headline about AAPL"] * 10
    
    start_time = time.perf_counter()
    embeddings = generator.batch_generate(texts)
    duration = time.perf_counter() - start_time
    
    print(f"\n⏱️ Embedding Generation (10 items): {duration:.4f}s")
    assert duration < MAX_EMBEDDING_TIME
    assert len(embeddings) == 10

@pytest.mark.benchmark
def test_vector_search_performance():
    """Benchmark Qdrant vector search latency."""
    # Note: Requires Qdrant to be running
    store = QdrantVectorStore()
    generator = EmbeddingGenerator()
    
    start_time = time.perf_counter()
    # We use a dummy query, assuming collection exists
    try:
        store.search_by_text("AAPL news", generator, ticker="AAPL", top_k=5)
    except Exception as e:
        pytest.skip(f"Qdrant not available or collection missing: {e}")
        
    duration = time.perf_counter() - start_time
    
    print(f"\n⏱️ Vector Search: {duration:.4f}s")
    assert duration < MAX_SEARCH_TIME

from unittest.mock import patch

@pytest.mark.benchmark
@patch("src.graph.ChatOllama")
def test_full_graph_execution_performance(mock_ollama):
    """Benchmark full agent graph execution (with mocked LLM)."""
    # Mock LLM response to avoid 100s+ inference time
    mock_llm_instance = mock_ollama.return_value
    mock_llm_instance.invoke.return_value.content = "Sentiment Score: 0.75\nReasoning: Positive news."

    app = create_graph()
    initial_state = {
        "messages": [HumanMessage(content="Analyze AAPL")],
        "market_data": pd.DataFrame(),
        "sentiment_score": 0.5,
        "trade_signal": TradeSignal.HOLD,
        "risk_approval": False,
        "execution_status": "PENDING"
    }
    
    start_time = time.perf_counter()
    # This runs the real graph with real tools (if not mocked)
    # For performance test, we want to measure real latency, so we don't mock here
    # BUT we need to be careful about rate limits. 
    # Ideally, we should use VCR.py to record network interactions, 
    # but for "system performance" including network I/O, we run it live.
    try:
        app.invoke(initial_state)
    except Exception as e:
        pytest.fail(f"Graph execution failed: {e}")
        
    duration = time.perf_counter() - start_time
    
    print(f"\n⏱️ Full Graph Execution: {duration:.4f}s")
    assert duration < MAX_GRAPH_EXECUTION_TIME
