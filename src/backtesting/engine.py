"""Backtesting engine for strategy evaluation.

Event-driven backtesting framework that replays historical data
and simulates trading with realistic transaction costs.
"""

from typing import Dict, List, Callable, Optional
from datetime import datetime
import pandas as pd

from src.backtesting.portfolio import Portfolio, Trade, OrderSide
from src.data.market_fetcher import MarketDataFetcher, DataFetchError


class BacktestEngine:
    """
    Event-driven backtesting engine.
    
    Replays historical market data chronologically and executes
    a trading strategy, tracking portfolio performance over time.
    """
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission_pct: float = 0.001,
        slippage_pct: float = 0.0005
    ):
        """
        Initialize backtest engine.
        
        Args:
            initial_capital: Starting portfolio value
            commission_pct: Commission as percentage of trade value
            slippage_pct: Slippage as percentage of price
        """
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct
        
        # Will be initialized when backtest runs
        self.portfolio: Optional[Portfolio] = None
        self.market_data: Dict[str, pd.DataFrame] = {}
        self.current_prices: Dict[str, float] = {}
        self.agent_logs: List[Dict] = [] # Store agent logs
    
    def load_historical_data(
        self,
        tickers: List[str],
        start_date: datetime,
        end_date: datetime,
        interval: str = '1d'
    ) -> None:
        """
        Load historical market data for backtesting.
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date for historical data
            end_date: End date for historical data
            interval: Data interval ('1d', '1h', '5m', etc.)
        """
        fetcher = MarketDataFetcher()
        self.market_data = {}
        
        for ticker in tickers:
            try:
                df = fetcher.fetch_ohlcv(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date,
                    interval=interval
                )
                self.market_data[ticker] = df
                print(f"✓ Loaded {len(df)} bars for {ticker}")
            except DataFetchError as e:
                print(f"✗ Failed to load {ticker}: {e}")
    
    def run(
        self,
        strategy_func: Callable[[datetime, Dict[str, pd.DataFrame], Portfolio], List[tuple[str, str, int]]],
        tickers: Optional[List[str]] = None
    ) -> Dict:
        """
        Run backtest with given strategy.
        
        Args:
            strategy_func: Strategy function that takes (timestamp, market_data, portfolio)
                          and returns list of (ticker, side, quantity) tuples
            tickers: Optional list of tickers to trade (defaults to all loaded tickers)
            
        Returns:
            Dictionary with backtest results
        """
        if not self.market_data:
            raise ValueError("No market data loaded. Call load_historical_data() first.")
        
        # Initialize portfolio
        self.portfolio = Portfolio(
            initial_capital=self.initial_capital,
            commission_pct=self.commission_pct,
            slippage_pct=self.slippage_pct
        )
        self.agent_logs = [] # Reset logs
        
        # Determine tickers to trade
        if tickers is None:
            tickers = list(self.market_data.keys())
        
        # Get all unique timestamps across all tickers
        all_timestamps = set()
        for df in self.market_data.values():
            all_timestamps.update(df['timestamp'].tolist())
        
        timestamps = sorted(all_timestamps)
        
        print(f"\n{'='*60}")
        print(f"Starting Backtest")
        print(f"{'='*60}")
        print(f"Period: {timestamps[0]} to {timestamps[-1]}")
        print(f"Tickers: {', '.join(tickers)}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"{'='*60}\n")
        
        # Event-driven simulation loop
        for i, timestamp in enumerate(timestamps):
            # Update current prices for all tickers
            self._update_current_prices(timestamp)
            
            # Record equity
            self.portfolio.record_equity(timestamp, self.current_prices)
            
            # Get market data up to current timestamp
            current_market_data = self._get_market_data_until(timestamp)
            
            # Call strategy function to get orders
            try:
                result = strategy_func(timestamp, current_market_data, self.portfolio)
                
                # Handle return value (list of orders OR tuple of (orders, logs))
                if isinstance(result, tuple):
                    orders, logs = result
                    # Add timestamp to logs and store
                    for log in logs:
                        log['step_timestamp'] = timestamp
                        self.agent_logs.append(log)
                else:
                    orders = result
                    
            except Exception as e:
                print(f"⚠ Strategy error at {timestamp}: {e}")
                continue
            
            # Execute orders
            if orders:
                self._execute_orders(orders, timestamp)
            
            # Progress indicator every 10%
            if (i + 1) % max(1, len(timestamps) // 10) == 0:
                progress = (i + 1) / len(timestamps) * 100
                equity = self.portfolio.get_equity(self.current_prices)
                print(f"Progress: {progress:.0f}% | Equity: ${equity:,.2f}")
        
        # Final equity recording
        final_equity = self.portfolio.get_equity(self.current_prices)
        
        print(f"\n{'='*60}")
        print(f"Backtest Complete")
        print(f"{'='*60}")
        print(f"Final Equity: ${final_equity:,.2f}")
        print(f"Total Return: {(final_equity / self.initial_capital - 1) * 100:.2f}%")
        print(f"Total Trades: {len(self.portfolio.trades)}")
        print(f"{'='*60}\n")
        
        return self._compile_results()
    
    def _update_current_prices(self, timestamp: datetime) -> None:
        """Update current prices for all tickers at given timestamp."""
        for ticker, df in self.market_data.items():
            # Find the most recent price at or before timestamp
            mask = df['timestamp'] <= timestamp
            if mask.any():
                latest_row = df[mask].iloc[-1]
                self.current_prices[ticker] = latest_row['close']
    
    def _get_market_data_until(self, timestamp: datetime) -> Dict[str, pd.DataFrame]:
        """Get market data for all tickers up to (and including) timestamp."""
        result = {}
        for ticker, df in self.market_data.items():
            mask = df['timestamp'] <= timestamp
            result[ticker] = df[mask].copy()
        return result
    
    def _execute_orders(self, orders: List[tuple[str, str, int]], timestamp: datetime) -> None:
        """Execute a list of orders."""
        for ticker, side, quantity in orders:
            if ticker not in self.current_prices:
                print(f"⚠ No price data for {ticker}, skipping order")
                continue
            
            price = self.current_prices[ticker]
            
            try:
                if side.upper() == 'BUY':
                    trade = self.portfolio.buy(ticker, quantity, price, timestamp)
                    print(f"✓ BUY {quantity} {ticker} @ ${price:.2f}")
                elif side.upper() == 'SELL':
                    trade = self.portfolio.sell(ticker, quantity, price, timestamp)
                    print(f"✓ SELL {quantity} {ticker} @ ${price:.2f}")
            except Exception as e:
                print(f"✗ Order failed: {e}")
    
    def _compile_results(self) -> Dict:
        """Compile backtest results into a dictionary."""
        equity_curve = pd.DataFrame(
            self.portfolio.equity_history,
            columns=['timestamp', 'equity']
        )
        
        trades_data = [
            {
                'timestamp': t.timestamp,
                'ticker': t.ticker,
                'side': t.side.value,
                'quantity': t.quantity,
                'price': t.price,
                'commission': t.commission,
                'slippage': t.slippage,
                'total_cost': t.total_cost
            }
            for t in self.portfolio.trades
        ]
        
        from src.backtesting.metrics import match_trades
        matched_trades = match_trades(trades_data)
        
        return {
            'equity_curve': equity_curve,
            'trades': trades_data,
            'matched_trades': matched_trades,
            'agent_logs': self.agent_logs, # Include logs
            'portfolio_summary': self.portfolio.get_summary(),
            'final_equity': self.portfolio.get_equity(self.current_prices),
            'total_return': (self.portfolio.get_equity(self.current_prices) / self.initial_capital - 1),
        }
