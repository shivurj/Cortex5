"""Pydantic models for news documents stored in Qdrant."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class NewsDocument(BaseModel):
    """Schema for news articles stored in the vector database."""
    
    id: str = Field(..., description="Unique identifier for the news article")
    ticker: str = Field(..., description="Stock ticker symbol this news relates to")
    title: str = Field(..., description="News article headline")
    content: str = Field(..., description="Full article text or description")
    published_at: datetime = Field(..., description="Publication timestamp")
    source: str = Field(..., description="News source name")
    url: Optional[str] = Field(None, description="URL to the full article")
    sentiment_label: Optional[str] = Field(
        None,
        description="Sentiment classification: 'positive', 'negative', or 'neutral'"
    )
    embedding: List[float] = Field(..., description="Vector embedding of the article")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123",
                "ticker": "AAPL",
                "title": "Apple Announces Record Quarterly Earnings",
                "content": "Apple Inc. reported record-breaking earnings...",
                "published_at": "2025-01-15T10:30:00Z",
                "source": "Bloomberg",
                "url": "https://example.com/article",
                "sentiment_label": "positive",
                "embedding": [0.1, 0.2, 0.3]  # Truncated for example
            }
        }


class SearchResult(BaseModel):
    """Schema for vector search results."""
    
    document: NewsDocument
    score: float = Field(..., description="Similarity score (0-1, higher is more similar)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document": {
                    "id": "abc123",
                    "ticker": "AAPL",
                    "title": "Apple Announces Record Quarterly Earnings",
                    "content": "Apple Inc. reported record-breaking earnings...",
                    "published_at": "2025-01-15T10:30:00Z",
                    "source": "Bloomberg",
                    "sentiment_label": "positive",
                    "embedding": []
                },
                "score": 0.95
            }
        }
