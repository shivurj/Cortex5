"""Market data fetcher for retrieving OHLCV data from Yahoo Finance."""

import time
from typing import Optional
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta


class DataFetchError(Exception):
    """Custom exception for data fetching errors."""
    pass


class MarketDataFetcher:
    """Fetches market data from Yahoo Finance with retry logic and error handling."""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize the market data fetcher.
        
        Args:
            max_retries: Maximum number of retry attempts for failed requests
            retry_delay: Initial delay between retries in seconds (uses exponential backoff)
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def _validate_interval_period(
        self,
        interval: str,
        period: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> None:
        """
        Validate interval and period compatibility.
        
        yfinance limitations:
        - Intraday data (1m, 5m, 15m, 30m, 1h) only available for last 60 days
        - Using custom date range with intraday requires dates within 60 days
        
        Raises:
            DataFetchError: If interval/period combination is invalid
        """
        intraday_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']
        
        if interval in intraday_intervals:
            # Check if using custom date range
            if start_date and end_date:
                days_diff = (end_date - start_date).days
                if days_diff > 60:
                    raise DataFetchError(
                        f"Intraday data (interval={interval}) only available for last 60 days. "
                        f"Requested range: {days_diff} days. Please reduce date range."
                    )
            else:
                # Check period validity for intraday
                valid_intraday_periods = ['1d', '5d', '1mo', '60d']
                if period not in valid_intraday_periods:
                    raise DataFetchError(
                        f"Period '{period}' not compatible with intraday interval '{interval}'. "
                        f"Valid periods for intraday: {valid_intraday_periods}"
                    )
    
    def fetch_ohlcv(
        self,
        ticker: str,
        period: str = "1mo",
        interval: str = "1d",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Fetch OHLCV (Open, High, Low, Close, Volume) data for a given ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
            period: Time period to fetch. Valid values: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            interval: Data interval. Valid values: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
            start_date: Optional start date for custom date range
            end_date: Optional end date for custom date range
            
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
            
        Raises:
            DataFetchError: If data cannot be fetched after retries or ticker is invalid
        """
        ticker = ticker.upper().strip()
        
        # Validate interval and period compatibility
        self._validate_interval_period(interval, period, start_date, end_date)
        
        for attempt in range(self.max_retries):
            try:
                # Create ticker object
                stock = yf.Ticker(ticker)
                
                # Fetch historical data
                if start_date and end_date:
                    df = stock.history(start=start_date, end=end_date, interval=interval)
                else:
                    df = stock.history(period=period, interval=interval)
                
                # Check if data was returned
                if df.empty:
                    raise DataFetchError(f"No data returned for ticker '{ticker}'. Ticker may be invalid.")
                
                # Reset index to make timestamp a column
                df = df.reset_index()
                
                # Rename columns to lowercase and standardize
                df = df.rename(columns={
                    'Date': 'timestamp',
                    'Datetime': 'timestamp',
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume'
                })
                
                # Select only required columns
                required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                df = df[required_columns]
                
                # Add symbol column
                df['symbol'] = ticker
                
                # Ensure timestamp is timezone-aware (UTC)
                if df['timestamp'].dt.tz is None:
                    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize('UTC')
                else:
                    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_convert('UTC')
                
                return df
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = self.retry_delay * (2 ** attempt)
                    print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    raise DataFetchError(
                        f"Failed to fetch data for '{ticker}' after {self.max_retries} attempts: {str(e)}"
                    )
        
        # This should never be reached, but for type safety
        raise DataFetchError(f"Unexpected error fetching data for '{ticker}'")
    
    def fetch_multiple(
        self,
        tickers: list[str],
        period: str = "1mo",
        interval: str = "1d"
    ) -> dict[str, pd.DataFrame]:
        """
        Fetch OHLCV data for multiple tickers.
        
        Args:
            tickers: List of ticker symbols
            period: Time period to fetch
            interval: Data interval
            
        Returns:
            Dictionary mapping ticker symbols to their DataFrames
        """
        results = {}
        
        for ticker in tickers:
            try:
                df = self.fetch_ohlcv(ticker, period, interval)
                results[ticker] = df
                print(f"✓ Successfully fetched {len(df)} rows for {ticker}")
            except DataFetchError as e:
                print(f"✗ Failed to fetch {ticker}: {str(e)}")
                results[ticker] = pd.DataFrame()  # Empty DataFrame for failed fetches
        
        return results
