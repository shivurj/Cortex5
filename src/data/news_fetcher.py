"""News fetcher for retrieving financial news from various sources."""

import os
import time
import hashlib
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
import feedparser
import requests


class NewsFetchError(Exception):
    """Custom exception for news fetching errors."""
    pass


class NewsFetcher:
    """Fetches financial news from NewsAPI and Google Finance RSS feeds."""
    
    def __init__(
        self,
        newsapi_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl_hours: int = 6
    ):
        """
        Initialize the news fetcher.
        
        Args:
            newsapi_key: NewsAPI key (optional, falls back to env var NEWS_API_KEY)
            cache_dir: Directory for caching news (default: .cache/news)
            cache_ttl_hours: Cache time-to-live in hours
        """
        self.newsapi_key = newsapi_key or os.getenv('NEWS_API_KEY')
        self.cache_dir = Path(cache_dir or '.cache/news')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        
        # Google Finance RSS feed template
        self.google_finance_rss = "https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
    
    def _get_cache_key(self, ticker: str, days_back: int) -> str:
        """Generate cache key for a ticker and date range."""
        key_str = f"{ticker}_{days_back}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _read_cache(self, cache_key: str) -> Optional[List[Dict]]:
        """Read news from cache if not expired."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        # Check if cache is expired
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        if file_age > self.cache_ttl:
            return None
        
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return None
    
    def _write_cache(self, cache_key: str, data: List[Dict]) -> None:
        """Write news to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except IOError as e:
            print(f"Warning: Failed to write cache: {e}")
    
    def fetch_from_google_finance(self, ticker: str) -> List[Dict]:
        """
        Fetch news from Google Finance RSS feed.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of news articles
        """
        url = self.google_finance_rss.format(ticker=ticker.upper())
        
        try:
            feed = feedparser.parse(url)
            
            articles = []
            for entry in feed.entries:
                # Parse published date
                published_at = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_at = datetime(*entry.published_parsed[:6])
                
                article = {
                    'title': entry.get('title', ''),
                    'description': entry.get('summary', ''),
                    'published_at': published_at or datetime.now(),
                    'url': entry.get('link', ''),
                    'source': 'Google Finance'
                }
                articles.append(article)
            
            return articles
            
        except Exception as e:
            raise NewsFetchError(f"Failed to fetch from Google Finance: {str(e)}")
    
    def fetch_from_newsapi(self, ticker: str, days_back: int = 7) -> List[Dict]:
        """
        Fetch news from NewsAPI.
        
        Args:
            ticker: Stock ticker symbol
            days_back: Number of days to look back
            
        Returns:
            List of news articles
            
        Raises:
            NewsFetchError: If API key is missing or request fails
        """
        if not self.newsapi_key:
            raise NewsFetchError(
                "NewsAPI key not provided. Set NEWS_API_KEY environment variable or pass to constructor."
            )
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # NewsAPI endpoint
        url = "https://newsapi.org/v2/everything"
        
        params = {
            'q': f'{ticker} stock OR {ticker} shares',
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'language': 'en',
            'sortBy': 'publishedAt',
            'apiKey': self.newsapi_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'ok':
                raise NewsFetchError(f"NewsAPI error: {data.get('message', 'Unknown error')}")
            
            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'published_at': datetime.fromisoformat(
                        article.get('publishedAt', '').replace('Z', '+00:00')
                    ) if article.get('publishedAt') else datetime.now(),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'Unknown')
                })
            
            return articles
            
        except requests.RequestException as e:
            raise NewsFetchError(f"Failed to fetch from NewsAPI: {str(e)}")
    
    def fetch_news(
        self,
        ticker: str,
        days_back: int = 7,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Fetch news for a ticker from all available sources.
        
        Args:
            ticker: Stock ticker symbol
            days_back: Number of days to look back
            use_cache: Whether to use cached results
            
        Returns:
            List of news articles with fields:
                - title: Article headline
                - description: Article summary
                - published_at: Publication datetime
                - url: Article URL
                - source: News source name
        """
        ticker = ticker.upper()
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(ticker, days_back)
            cached_news = self._read_cache(cache_key)
            if cached_news:
                print(f"✓ Using cached news for {ticker} ({len(cached_news)} articles)")
                return cached_news
        
        all_articles = []
        
        # Try Google Finance RSS (free, no API key needed)
        try:
            google_articles = self.fetch_from_google_finance(ticker)
            all_articles.extend(google_articles)
            print(f"✓ Fetched {len(google_articles)} articles from Google Finance")
        except NewsFetchError as e:
            print(f"⚠ Google Finance fetch failed: {e}")
        
        # Try NewsAPI if key is available
        if self.newsapi_key:
            try:
                newsapi_articles = self.fetch_from_newsapi(ticker, days_back)
                all_articles.extend(newsapi_articles)
                print(f"✓ Fetched {len(newsapi_articles)} articles from NewsAPI")
            except NewsFetchError as e:
                print(f"⚠ NewsAPI fetch failed: {e}")
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            title_lower = article['title'].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_articles.append(article)
        
        # Filter by date range
        cutoff_date = datetime.now() - timedelta(days=days_back)
        filtered_articles = [
            article for article in unique_articles
            if article['published_at'] >= cutoff_date
        ]
        
        # Sort by published date (newest first)
        filtered_articles.sort(key=lambda x: x['published_at'], reverse=True)
        
        # Write to cache
        if use_cache and filtered_articles:
            cache_key = self._get_cache_key(ticker, days_back)
            self._write_cache(cache_key, filtered_articles)
        
        print(f"✓ Total unique articles for {ticker}: {len(filtered_articles)}")
        return filtered_articles
    
    def fetch_multiple(
        self,
        tickers: List[str],
        days_back: int = 7,
        use_cache: bool = True,
        delay_between_requests: float = 1.0
    ) -> Dict[str, List[Dict]]:
        """
        Fetch news for multiple tickers.
        
        Args:
            tickers: List of ticker symbols
            days_back: Number of days to look back
            use_cache: Whether to use cached results
            delay_between_requests: Delay in seconds between API calls
            
        Returns:
            Dictionary mapping tickers to their news articles
        """
        results = {}
        
        for i, ticker in enumerate(tickers):
            try:
                articles = self.fetch_news(ticker, days_back, use_cache)
                results[ticker] = articles
                
                # Add delay between requests to avoid rate limiting
                if i < len(tickers) - 1:
                    time.sleep(delay_between_requests)
                    
            except Exception as e:
                print(f"✗ Failed to fetch news for {ticker}: {e}")
                results[ticker] = []
        
        return results
