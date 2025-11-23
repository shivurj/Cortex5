"""Qdrant vector store client for news article storage and retrieval."""

import os
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime
from qdrant_client import QdrantClient as QdrantClientSDK
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest
)
from src.data.vector_schema import NewsDocument, SearchResult


class VectorStoreError(Exception):
    """Custom exception for vector store operations."""
    pass


class QdrantVectorStore:
    """Client for interacting with Qdrant vector database."""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        collection_name: str = "financial_news"
    ):
        """
        Initialize Qdrant vector store client.
        
        Args:
            host: Qdrant host (defaults to env var QDRANT_HOST or 'localhost')
            port: Qdrant port (defaults to env var QDRANT_PORT or 6333)
            collection_name: Name of the collection to use
        """
        self.host = host or os.getenv('QDRANT_HOST', 'localhost')
        self.port = port or int(os.getenv('QDRANT_PORT', '6333'))
        self.collection_name = collection_name
        
        try:
            self.client = QdrantClientSDK(host=self.host, port=self.port)
            print(f"✓ Connected to Qdrant at {self.host}:{self.port}")
        except Exception as e:
            raise VectorStoreError(f"Failed to connect to Qdrant: {str(e)}")
    
    def create_collection(
        self,
        collection_name: Optional[str] = None,
        vector_size: int = 384,
        distance: Distance = Distance.COSINE,
        recreate: bool = False
    ) -> None:
        """
        Create a new collection in Qdrant.
        
        Args:
            collection_name: Name of the collection (uses default if None)
            vector_size: Dimension of the embedding vectors
            distance: Distance metric (COSINE, EUCLID, DOT)
            recreate: If True, delete existing collection and create new one
            
        Raises:
            VectorStoreError: If collection creation fails
        """
        collection_name = collection_name or self.collection_name
        
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)
            
            if exists:
                if recreate:
                    print(f"⚠ Deleting existing collection '{collection_name}'")
                    self.client.delete_collection(collection_name)
                else:
                    print(f"✓ Collection '{collection_name}' already exists")
                    return
            
            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance
                )
            )
            print(f"✓ Created collection '{collection_name}' (dim={vector_size}, distance={distance.value})")
            
        except Exception as e:
            raise VectorStoreError(f"Failed to create collection: {str(e)}")
    
    def upsert_documents(
        self,
        documents: List[NewsDocument],
        collection_name: Optional[str] = None
    ) -> int:
        """
        Insert or update documents in the collection.
        
        Args:
            documents: List of NewsDocument objects to upsert
            collection_name: Collection to upsert into (uses default if None)
            
        Returns:
            Number of documents upserted
            
        Raises:
            VectorStoreError: If upsert fails
        """
        if not documents:
            return 0
        
        collection_name = collection_name or self.collection_name
        
        try:
            # Convert documents to Qdrant points
            points = []
            for doc in documents:
                # Create payload (all fields except embedding)
                payload = {
                    "ticker": doc.ticker,
                    "title": doc.title,
                    "content": doc.content,
                    "published_at": doc.published_at.isoformat(),
                    "source": doc.source,
                    "url": doc.url,
                    "sentiment_label": doc.sentiment_label
                }
                
                # Create point
                point = PointStruct(
                    id=doc.id,
                    vector=doc.embedding,
                    payload=payload
                )
                points.append(point)
            
            # Upsert points
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            print(f"✓ Upserted {len(points)} documents to '{collection_name}'")
            return len(points)
            
        except Exception as e:
            raise VectorStoreError(f"Failed to upsert documents: {str(e)}")
    
    def search_similar(
        self,
        query_vector: List[float],
        ticker: Optional[str] = None,
        top_k: int = 5,
        score_threshold: Optional[float] = None,
        collection_name: Optional[str] = None,
        published_before: Optional[datetime] = None
    ) -> List[SearchResult]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query_vector: Query embedding vector
            ticker: Filter results by ticker symbol (optional)
            top_k: Number of results to return
            score_threshold: Minimum similarity score (0-1)
            collection_name: Collection to search (uses default if None)
            published_before: Filter for news published before this time
            
        Returns:
            List of SearchResult objects
            
        Raises:
            VectorStoreError: If search fails
        """
        collection_name = collection_name or self.collection_name
        
        try:
            # Build filter
            must_conditions = []
            
            # Ticker filter
            if ticker:
                must_conditions.append(
                    FieldCondition(
                        key="ticker",
                        match=MatchValue(value=ticker.upper())
                    )
                )
            
            # Date filter (prevent look-ahead bias)
            if published_before:
                from qdrant_client.models import Range
                must_conditions.append(
                    FieldCondition(
                        key="published_at",
                        range=Range(
                            lte=published_before.isoformat()
                        )
                    )
                )
            
            query_filter = None
            if must_conditions:
                query_filter = Filter(must=must_conditions)
            
            # Perform search
            try:
                search_results = self.client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    query_filter=query_filter,
                    limit=top_k,
                    score_threshold=score_threshold
                )
            except AttributeError:
                # Fallback for older Qdrant client versions or specific configurations
                # where `search` might not directly accept `query_vector` or `query_filter`
                # and `query_points` is used.
                # Note: `query_points` expects `query` instead of `query_vector`.
                search_results = self.client.query_points(
                    collection_name=collection_name,
                    query=query_vector,
                    query_filter=query_filter,
                    limit=top_k,
                    score_threshold=score_threshold
                ).points
            
            # Convert to SearchResult objects
            results = []
            for hit in search_results:
                # Reconstruct NewsDocument
                doc = NewsDocument(
                    id=str(hit.id),
                    ticker=hit.payload["ticker"],
                    title=hit.payload["title"],
                    content=hit.payload["content"],
                    published_at=datetime.fromisoformat(hit.payload["published_at"]),
                    source=hit.payload["source"],
                    url=hit.payload.get("url"),
                    sentiment_label=hit.payload.get("sentiment_label"),
                    embedding=hit.vector or []
                )
                
                results.append(SearchResult(document=doc, score=hit.score))
            
            return results
            
        except Exception as e:
            raise VectorStoreError(f"Failed to search documents: {str(e)}")
    
    def search_by_text(
        self,
        query_text: str,
        embedding_generator,
        ticker: Optional[str] = None,
        top_k: int = 5,
        collection_name: Optional[str] = None,
        published_before: Optional[datetime] = None
    ) -> List[SearchResult]:
        """
        Search for similar documents using text query.
        
        Args:
            query_text: Text query to search for
            embedding_generator: EmbeddingGenerator instance to encode query
            ticker: Filter results by ticker symbol (optional)
            top_k: Number of results to return
            collection_name: Collection to search (uses default if None)
            published_before: Filter for news published before this time
            
        Returns:
            List of SearchResult objects
        """
        # Generate embedding for query text
        query_vector = embedding_generator.generate_embedding(query_text)
        
        # Perform vector search
        return self.search_similar(
            query_vector=query_vector,
            ticker=ticker,
            top_k=top_k,
            collection_name=collection_name,
            published_before=published_before
        )
    
    def get_collection_info(
        self,
        collection_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get information about a collection.
        
        Args:
            collection_name: Collection name (uses default if None)
            
        Returns:
            Dictionary with collection statistics
        """
        collection_name = collection_name or self.collection_name
        
        try:
            info = self.client.get_collection(collection_name)
            
            return {
                "name": collection_name,
                "vectors_count": getattr(info, "vectors_count", None),
                "points_count": info.points_count,
                "status": info.status.value,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance.value
            }
        except Exception as e:
            raise VectorStoreError(f"Failed to get collection info: {str(e)}")
    
    def delete_by_ticker(
        self,
        ticker: str,
        collection_name: Optional[str] = None
    ) -> None:
        """
        Delete all documents for a specific ticker.
        
        Args:
            ticker: Ticker symbol to delete
            collection_name: Collection name (uses default if None)
        """
        collection_name = collection_name or self.collection_name
        
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="ticker",
                            match=MatchValue(value=ticker.upper())
                        )
                    ]
                )
            )
            print(f"✓ Deleted all documents for ticker '{ticker}'")
        except Exception as e:
            raise VectorStoreError(f"Failed to delete documents: {str(e)}")


def generate_document_id(ticker: str, title: str, published_at: datetime) -> str:
    """
    Generate a unique ID for a news document.
    
    Args:
        ticker: Stock ticker
        title: Article title
        published_at: Publication datetime
        
    Returns:
        Unique document ID (MD5 hash)
    """
    # Create unique string from ticker, title, and timestamp
    unique_str = f"{ticker}_{title}_{published_at.isoformat()}"
    
    # Generate MD5 hash
    return hashlib.md5(unique_str.encode()).hexdigest()
