from typing import Dict, Any
import pandas as pd
from langchain_core.messages import AIMessage
from src.agents.base_agent import BaseAgent
from src.state import AgentState
from src.data.market_fetcher import MarketDataFetcher, DataFetchError
from src.data.validators import validate_ohlcv_data, DataValidationError
from src.data.db_client import TimescaleDBClient, DatabaseError


class DataAgent(BaseAgent):
    """Data Agent responsible for fetching and storing market data."""
    
    def __init__(self, model):
        super().__init__(
            name="DataAgent",
            model=model,
            tools=[]
        )
        self.system_prompt = (
            "You are the Data Engineer. Your job is to fetch raw OHLCV data from Yahoo Finance "
            "and store it in TimescaleDB. You do not analyze, you only provide facts."
        )
        
        # Initialize data fetcher and database client
        self.fetcher = MarketDataFetcher()
        self.db_client = None
    
    def _ensure_db_connection(self):
        """Ensure database connection is established."""
        if self.db_client is None:
            try:
                self.db_client = TimescaleDBClient()
                self.db_client.connect()
            except DatabaseError as e:
                print(f"⚠ Database connection failed: {e}")
                self.db_client = None
    
    def run(self, state: AgentState) -> Dict[str, Any]:
        """
        Fetch market data and store in database.
        
        Extracts ticker from the user's message, fetches OHLCV data,
        validates it, stores in TimescaleDB, and updates state.
        """
        print(f"\n{'='*60}")
        print(f"🔵 {self.name} Starting")
        print(f"{'='*60}")
        
        # Extract ticker from messages
        ticker = self._extract_ticker(state)
        
        if not ticker:
            error_msg = "Could not extract ticker symbol from message"
            print(f"✗ {error_msg}")
            return {
                "messages": [AIMessage(content=error_msg)],
                "market_data": {}
            }
        
        print(f"📊 Ticker: {ticker}")
        
        # Check if data already exists in database
        self._ensure_db_connection()
        
        if self.db_client:
            try:
                existing_data = self.db_client.query_market_data(ticker, limit=30)
                if not existing_data.empty:
                    print(f"✓ Found {len(existing_data)} existing records in database")
                    return {
                        "messages": [AIMessage(content=f"Retrieved {len(existing_data)} records for {ticker} from database")],
                        "market_data": existing_data
                    }
            except DatabaseError as e:
                print(f"⚠ Database query failed: {e}")
        
        # Fetch fresh data from Yahoo Finance
        try:
            print(f"📥 Fetching data from Yahoo Finance...")
            df = self.fetcher.fetch_ohlcv(ticker, period="3mo", interval="1d")
            print(f"✓ Fetched {len(df)} rows")
            
            # Validate data
            print(f"🔍 Validating data...")
            validate_ohlcv_data(df)
            print(f"✓ Data validation passed")
            
            # Store in database if available
            if self.db_client:
                try:
                    self.db_client.insert_market_data(df)
                except DatabaseError as e:
                    print(f"⚠ Failed to store in database: {e}")
            
            return {
                "messages": [AIMessage(content=f"Successfully fetched and validated {len(df)} records for {ticker}")],
                "market_data": df
            }
            
        except (DataFetchError, DataValidationError) as e:
            error_msg = f"Failed to fetch/validate data for {ticker}: {str(e)}"
            print(f"✗ {error_msg}")
            return {
                "messages": [AIMessage(content=error_msg)],
                "market_data": pd.DataFrame()
            }
    
    def _extract_ticker(self, state: AgentState) -> str:
        """Extract ticker symbol from the user's message."""
        messages = state.get("messages", [])
        if not messages:
            return ""
        
        # Get the first message content
        content = messages[0].content.upper()
        
        # Simple extraction - look for common ticker patterns
        # This could be enhanced with NLP
        words = content.split()
        for word in words:
            # Remove common words and punctuation
            clean_word = word.strip('.,!?;:')
            # Check if it looks like a ticker (2-5 uppercase letters)
            if clean_word.isalpha() and 2 <= len(clean_word) <= 5:
                return clean_word
        
        return ""
