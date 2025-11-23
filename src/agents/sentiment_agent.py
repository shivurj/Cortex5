from typing import Dict, Any
from langchain_core.messages import AIMessage
from src.agents.base_agent import BaseAgent
from src.state import AgentState
from src.data.qdrant_client import QdrantVectorStore, VectorStoreError
from src.data.embeddings import EmbeddingGenerator, EmbeddingError


class SentimentAgent(BaseAgent):
    """Sentiment Agent responsible for RAG-based sentiment analysis."""
    
    def __init__(self, model, callback=None):
        super().__init__(
            name="SentimentAgent",
            model=model,
            tools=[],
            callback=callback
        )
        self.system_prompt = (
            "You are the Sentiment Analyst. Your job is to read news headlines and output a sentiment score "
            "between 0 (Bearish) and 1 (Bullish). You use the Qdrant vector DB to find similar historical news."
        )
        
        # Initialize vector store and embedding generator
        self.vector_store = None
        self.embedding_gen = None
    
    def _ensure_connections(self):
        """Ensure vector store and embedding generator are initialized."""
        if self.vector_store is None:
            try:
                self.vector_store = QdrantVectorStore()
            except VectorStoreError as e:
                print(f"⚠ Qdrant connection failed: {e}")
                self.vector_store = None
        
        if self.embedding_gen is None:
            try:
                self.embedding_gen = EmbeddingGenerator()
            except EmbeddingError as e:
                print(f"⚠ Embedding generator initialization failed: {e}")
                self.embedding_gen = None
    
    def run(self, state: AgentState) -> Dict[str, Any]:
        """
        Perform RAG-based sentiment analysis.
        
        Retrieves relevant news from Qdrant and uses LLM to analyze sentiment.
        """
        self.log("Starting sentiment analysis...", "status")
        
        # Extract ticker from market data
        market_data = state.get("market_data", {})
        if isinstance(market_data, dict) or (hasattr(market_data, 'empty') and market_data.empty):
            print("⚠ No market data available, using neutral sentiment")
            return {
                "messages": [AIMessage(content="No market data available for sentiment analysis")],
                "sentiment_score": 0.5
            }
        
        ticker = market_data['symbol'].iloc[0] if 'symbol' in market_data.columns else None
        
        if not ticker:
            print("⚠ Could not extract ticker, using neutral sentiment")
            return {
                "messages": [AIMessage(content="Could not determine ticker for sentiment analysis")],
                "sentiment_score": 0.5
            }
        
        self.log(f"Analyzing sentiment for: {ticker}", "info")
        
        # Ensure connections
        self._ensure_connections()
        
        if not self.vector_store or not self.embedding_gen:
            print("⚠ Vector store or embedding generator not available, using neutral sentiment")
            return {
                "messages": [AIMessage(content="Sentiment analysis tools not available")],
                "sentiment_score": 0.5
            }
        
        # Query for relevant news
        try:
            self.log(f"Searching for news about {ticker}...", "status")
            query_text = f"news about {ticker} stock market performance"
            
            results = self.vector_store.search_by_text(
                query_text=query_text,
                embedding_generator=self.embedding_gen,
                ticker=ticker,
                top_k=5
            )
            
            if not results:
                print(f"⚠ No news found for {ticker}, using neutral sentiment")
                return {
                    "messages": [AIMessage(content=f"No recent news found for {ticker}")],
                    "sentiment_score": 0.5
                }
            
            self.log(f"Found {len(results)} relevant news articles", "success")
            
            # Prepare news context for LLM
            news_context = "\n\n".join([
                f"[{i+1}] {result.document.title} ({result.document.source}, {result.document.published_at.strftime('%Y-%m-%d')})\n"
                f"    {result.document.content[:200]}..."
                for i, result in enumerate(results)
            ])
            
            # Use LLM to analyze sentiment
            prompt = f"""Based on these recent news headlines about {ticker}, provide a sentiment score from 0.0 (very bearish) to 1.0 (very bullish).

News Articles:
{news_context}

Consider:
- Market impact and significance
- Tone and language used
- Overall trend in the news

Respond with ONLY a number between 0.0 and 1.0, nothing else."""
            
            # Get LLM response
            response = self.model.invoke(prompt)
            
            # Parse sentiment score
            try:
                sentiment_score = float(response.content.strip())
                sentiment_score = max(0.0, min(1.0, sentiment_score))  # Clamp to [0, 1]
            except ValueError:
                print(f"⚠ Could not parse sentiment score from LLM response: {response.content}")
                sentiment_score = 0.5
            
            # Determine sentiment label
            if sentiment_score >= 0.6:
                label = "Bullish"
            elif sentiment_score <= 0.4:
                label = "Bearish"
            else:
                label = "Neutral"
            
            self.log(f"Sentiment Score: {sentiment_score:.2f} ({label})", "success", {"score": sentiment_score, "label": label})
            
            return {
                "messages": [AIMessage(content=f"Sentiment analysis for {ticker}: {label} (score: {sentiment_score:.2f})")],
                "sentiment_score": sentiment_score
            }
            
        except (VectorStoreError, EmbeddingError) as e:
            print(f"✗ Sentiment analysis failed: {e}")
            return {
                "messages": [AIMessage(content=f"Sentiment analysis error: {str(e)}")],
                "sentiment_score": 0.5
            }
