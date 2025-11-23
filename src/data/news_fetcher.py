"""News fetcher for retrieving financial news from external sources."""

import yfinance as yf
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from src.data.vector_schema import NewsDocument
from src.data.qdrant_client import generate_document_id

class NewsFetcher:
    """
    Fetcher for financial news using yfinance and other sources.
    """
    
    def __init__(self):
        """Initialize news fetcher."""
        pass
        
    def fetch_news(self, ticker: str, limit: int = 5) -> List[NewsDocument]:
        """
        Fetch recent news for a ticker using yfinance.
        
        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of articles to return
            
        Returns:
            List of NewsDocument objects
        """
        try:
            stock = yf.Ticker(ticker)
            news_data = stock.news
            
            documents = []
            for item in news_data[:limit]:
                # Parse timestamp
                # yfinance returns unix timestamp in 'providerPublishTime'
                published_at = datetime.fromtimestamp(item.get('providerPublishTime', 0))
                
                title = item.get('title', '')
                link = item.get('link', '')
                publisher = item.get('publisher', 'Unknown')
                
                # Create document
                doc = NewsDocument(
                    id=generate_document_id(ticker, title, published_at),
                    ticker=ticker,
                    title=title,
                    content=title, # yfinance often only gives title/link, no full content
                    published_at=published_at,
                    source=publisher,
                    url=link,
                    sentiment_label=None,
                    embedding=None
                )
                documents.append(doc)
                
            print(f"✓ Fetched {len(documents)} news articles for {ticker}")
            return documents
            
        except Exception as e:
            print(f"✗ Failed to fetch news for {ticker}: {e}")
            return []

    def fetch_historical_news(self, ticker: str, start_date: datetime, end_date: datetime) -> List[NewsDocument]:
        """
        Fetch historical news (Placeholder - yfinance doesn't support history well).
        
        Args:
            ticker: Stock ticker
            start_date: Start date
            end_date: End date
            
        Returns:
            List of NewsDocument objects
        """
        # Note: yfinance news is limited to recent items.
        # For true historical news, we'd need a paid API like Polygon.io or NewsAPI.
        # For this demo, we'll just return recent news if it falls in range.
        
        all_news = self.fetch_news(ticker, limit=20)
        
        filtered_news = []
        for doc in all_news:
            if start_date <= doc.published_at <= end_date:
                filtered_news.append(doc)
                
        return filtered_news
