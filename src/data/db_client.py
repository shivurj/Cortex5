"""TimescaleDB client for market data and trade log storage."""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd
import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import execute_values
from contextlib import contextmanager


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


class TimescaleDBClient:
    """Client for interacting with TimescaleDB for market data storage."""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        min_conn: int = 1,
        max_conn: int = 10
    ):
        """
        Initialize TimescaleDB client with connection pooling.
        
        Args:
            host: Database host (defaults to env var DB_HOST or 'localhost')
            port: Database port (defaults to env var DB_PORT or 5432)
            database: Database name (defaults to env var DB_NAME or 'postgres')
            user: Database user (defaults to env var DB_USER or 'postgres')
            password: Database password (defaults to env var DB_PASSWORD or 'password')
            min_conn: Minimum connections in pool
            max_conn: Maximum connections in pool
        """
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or int(os.getenv('DB_PORT', '5432'))
        self.database = database or os.getenv('DB_NAME', 'postgres')
        self.user = user or os.getenv('DB_USER', 'postgres')
        self.password = password or os.getenv('DB_PASSWORD', 'password')
        
        self.connection_pool = None
        self.min_conn = min_conn
        self.max_conn = max_conn
    
    def connect(self) -> None:
        """
        Establish connection pool to the database.
        
        Raises:
            DatabaseError: If connection fails
        """
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                self.min_conn,
                self.max_conn,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print(f"✓ Connected to TimescaleDB at {self.host}:{self.port}/{self.database}")
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to connect to database: {str(e)}")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for getting a connection from the pool.
        
        Yields:
            Database connection
        """
        if self.connection_pool is None:
            self.connect()
        
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)
    
    def insert_market_data(self, df: pd.DataFrame) -> int:
        """
        Bulk insert OHLCV market data into the database.
        
        Args:
            df: DataFrame with columns: symbol, timestamp, open, high, low, close, volume
            
        Returns:
            Number of rows inserted
            
        Raises:
            DatabaseError: If insertion fails
        """
        if df.empty:
            return 0
        
        required_columns = ['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise DatabaseError(f"Missing required columns: {missing}")
        
        # Prepare data for insertion
        # Convert DataFrame to list of tuples with explicit type casting
        # psycopg2 doesn't handle numpy types well, so we cast to native types
        data = []
        for row in df[required_columns].itertuples(index=False):
            data.append((
                str(row.symbol),
                row.timestamp,
                float(row.open),
                float(row.high),
                float(row.low),
                float(row.close),
                int(row.volume)
            ))
        
        query = """
            INSERT INTO market_data (symbol, timestamp, open, high, low, close, volume)
            VALUES %s
            ON CONFLICT (symbol, timestamp) DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    execute_values(cursor, query, data)
                    conn.commit()
                    rows_affected = cursor.rowcount
                    print(f"✓ Inserted/updated {rows_affected} market data rows")
                    return rows_affected
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to insert market data: {str(e)}")
    
    def query_market_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Query market data for a specific symbol and date range.
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date for query (inclusive)
            end_date: End date for query (inclusive)
            limit: Maximum number of rows to return
            
        Returns:
            DataFrame with market data
            
        Raises:
            DatabaseError: If query fails
        """
        query = """
            SELECT symbol, timestamp, open, high, low, close, volume
            FROM market_data
            WHERE symbol = %s
        """
        params = [symbol.upper()]
        
        if start_date:
            query += " AND timestamp >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= %s"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)
                return df
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to query market data: {str(e)}")
    
    def log_trade(
        self,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
        status: str = "EXECUTED",
        sentiment_score: Optional[float] = None,
        trade_signal: Optional[str] = None,
        risk_approved: bool = False,
        notes: Optional[str] = None
    ) -> int:
        """
        Log a trade execution to the database.
        
        Args:
            symbol: Stock ticker symbol
            side: 'BUY' or 'SELL'
            quantity: Number of shares
            price: Execution price per share
            status: Trade status (default: 'EXECUTED')
            sentiment_score: Sentiment score at time of trade
            trade_signal: Signal that triggered the trade
            risk_approved: Whether risk checks passed
            notes: Additional notes
            
        Returns:
            Trade log ID
            
        Raises:
            DatabaseError: If logging fails
        """
        query = """
            INSERT INTO trade_logs 
            (symbol, side, quantity, price, status, sentiment_score, trade_signal, risk_approved, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        query,
                        (symbol.upper(), side.upper(), quantity, price, status,
                         sentiment_score, trade_signal, risk_approved, notes)
                    )
                    trade_id = cursor.fetchone()[0]
                    conn.commit()
                    print(f"✓ Logged trade: {side} {quantity} {symbol} @ ${price:.2f} (ID: {trade_id})")
                    return trade_id
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to log trade: {str(e)}")
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get the most recent closing price for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Latest close price or None if not found
        """
        query = """
            SELECT close 
            FROM market_data 
            WHERE symbol = %s 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (symbol.upper(),))
                    result = cursor.fetchone()
                    return float(result[0]) if result else None
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to get latest price: {str(e)}")
    
    def get_portfolio_value(self) -> float:
        """
        Calculate total portfolio value (holdings + cash).
        
        Returns:
            Total portfolio value in dollars
        """
        query = "SELECT get_portfolio_value()"
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchone()
                    return float(result[0]) if result else 0.0
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to get portfolio value: {str(e)}")
    
    def execute_sql_file(self, filepath: str) -> None:
        """
        Execute SQL commands from a file.
        
        Args:
            filepath: Path to SQL file
            
        Raises:
            DatabaseError: If execution fails
        """
        try:
            with open(filepath, 'r') as f:
                sql_commands = f.read()
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_commands)
                    conn.commit()
                    print(f"✓ Executed SQL file: {filepath}")
        except (IOError, psycopg2.Error) as e:
            raise DatabaseError(f"Failed to execute SQL file: {str(e)}")
    
    def close(self) -> None:
        """Close all connections in the pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✓ Closed all database connections")
