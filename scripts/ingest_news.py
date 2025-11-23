#!/usr/bin/env python3
"""News ingestion pipeline for Cortex5 AI Hedge Fund."""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.news_fetcher import NewsFetcher, NewsFetchError
from src.data.embeddings import EmbeddingGenerator, EmbeddingError
from src.data.qdrant_client import QdrantVectorStore, VectorStoreError, generate_document_id
from src.data.vector_schema import NewsDocument


def main():
    """Main news ingestion pipeline."""
    parser = argparse.ArgumentParser(description="Ingest financial news into Qdrant vector store")
    parser.add_argument(
        '--tickers',
        type=str,
        required=True,
        help='Comma-separated list of ticker symbols (e.g., AAPL,GOOGL,MSFT)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to look back for news (default: 7)'
    )
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable caching of news articles'
    )
    parser.add_argument(
        '--recreate-collection',
        action='store_true',
        help='Delete and recreate the Qdrant collection'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Batch size for embedding generation (default: 32)'
    )
    
    args = parser.parse_args()
    
    # Parse tickers
    tickers = [t.strip().upper() for t in args.tickers.split(',')]
    
    print("=" * 70)
    print("Cortex5 News Ingestion Pipeline")
    print("=" * 70)
    print(f"\n📊 Tickers: {', '.join(tickers)}")
    print(f"📅 Days back: {args.days}")
    print(f"💾 Cache: {'Disabled' if args.no_cache else 'Enabled'}")
    print()
    
    try:
        # Initialize components
        print("🔧 Initializing components...")
        news_fetcher = NewsFetcher()
        embedding_gen = EmbeddingGenerator()
        vector_store = QdrantVectorStore()
        
        # Create or verify collection
        print(f"\n📦 Setting up Qdrant collection...")
        vector_store.create_collection(
            vector_size=embedding_gen.get_embedding_dimension(),
            recreate=args.recreate_collection
        )
        
        # Fetch news for all tickers
        print(f"\n📰 Fetching news articles...")
        all_news = news_fetcher.fetch_multiple(
            tickers=tickers,
            days_back=args.days,
            use_cache=not args.no_cache
        )
        
        # Process each ticker
        total_articles = 0
        total_embedded = 0
        
        for ticker, articles in all_news.items():
            if not articles:
                print(f"\n⚠ No articles found for {ticker}")
                continue
            
            print(f"\n🔄 Processing {len(articles)} articles for {ticker}...")
            
            # Prepare texts for embedding
            texts = []
            article_metadata = []
            
            for article in articles:
                # Combine title and description for embedding
                text = f"{article['title']}. {article['description']}"
                texts.append(text)
                article_metadata.append(article)
            
            # Generate embeddings in batch
            print(f"  🧠 Generating embeddings...")
            try:
                embeddings = embedding_gen.batch_generate(
                    texts,
                    batch_size=args.batch_size,
                    show_progress=True
                )
            except EmbeddingError as e:
                print(f"  ✗ Failed to generate embeddings: {e}")
                continue
            
            # Create NewsDocument objects
            documents = []
            for article, embedding in zip(article_metadata, embeddings):
                doc_id = generate_document_id(
                    ticker,
                    article['title'],
                    article['published_at']
                )
                
                doc = NewsDocument(
                    id=doc_id,
                    ticker=ticker,
                    title=article['title'],
                    content=article['description'],
                    published_at=article['published_at'],
                    source=article['source'],
                    url=article.get('url'),
                    sentiment_label=None,  # Will be filled by sentiment agent
                    embedding=embedding
                )
                documents.append(doc)
            
            # Upsert to Qdrant
            print(f"  💾 Storing in Qdrant...")
            try:
                count = vector_store.upsert_documents(documents)
                total_embedded += count
            except VectorStoreError as e:
                print(f"  ✗ Failed to store documents: {e}")
                continue
            
            total_articles += len(articles)
        
        # Print summary
        print("\n" + "=" * 70)
        print("✅ Ingestion Complete!")
        print("=" * 70)
        print(f"📊 Total articles fetched: {total_articles}")
        print(f"🧠 Total articles embedded: {total_embedded}")
        
        # Show collection info
        print(f"\n📦 Collection Info:")
        info = vector_store.get_collection_info()
        for key, value in info.items():
            print(f"  • {key}: {value}")
        
        print("\n" + "=" * 70)
        
    except NewsFetchError as e:
        print(f"\n✗ News fetch error: {e}")
        sys.exit(1)
    except EmbeddingError as e:
        print(f"\n✗ Embedding error: {e}")
        sys.exit(1)
    except VectorStoreError as e:
        print(f"\n✗ Vector store error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
