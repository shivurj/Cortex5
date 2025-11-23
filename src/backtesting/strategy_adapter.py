"""Strategy adapter for integrating agent-based trading with backtesting engine.

Wraps the LangGraph agent pipeline to work with the backtesting framework.
"""

from typing import Dict, List, Callable, Optional
from datetime import datetime
import pandas as pd

from src.graph import create_graph
from src.backtesting.portfolio import Portfolio


class AgentStrategy:
    """
    Adapter that wraps the agent graph for use in backtesting.
    
    Converts backtest events to agent state format and extracts
    trade signals from agent output.
    """
    
    def __init__(self, callback: Optional[Callable] = None):
        """
        Initialize agent strategy.
        
        Args:
            callback: Optional callback for agent events
        """
        self.external_callback = callback
        self.current_logs = []
        
        # Create internal callback that captures logs and calls external callback
        def log_capturer(payload):
            self.current_logs.append(payload)
            if self.external_callback:
                self.external_callback(payload)
                
        self.graph = create_graph(callback=log_capturer)
        self.last_signals = {}  # Track last signal per ticker
    
    def generate_signals(
        self,
        timestamp: datetime,
        market_data: Dict[str, pd.DataFrame],
        portfolio: Portfolio
    ) -> tuple[List[tuple[str, str, int]], List[Dict]]:
        """
        Generate trading signals using the agent graph.
        
        Args:
            timestamp: Current timestamp
            market_data: Market data for all tickers
            portfolio: Current portfolio state
            
        Returns:
            Tuple of (orders, logs)
        """
        orders = []
        self.current_logs = [] # Clear logs for this step
        
        # Process each ticker through the agent pipeline
        for ticker, df in market_data.items():
            if len(df) < 2:
                continue
            
            # Prepare agent state
            from langchain_core.messages import HumanMessage
            initial_state = {
                "messages": [HumanMessage(content=f"Analyze {ticker}")],
                "data": {"ticker": ticker},
                "market_data": df  # Inject sliced market data
            }
            
            try:
                # Run agent graph
                result = self.graph.invoke(initial_state)
                
                # Extract trade signal
                signal = result.get('trade_signal', 'HOLD')
                
                # Only act on signal changes or new signals
                if signal != self.last_signals.get(ticker, 'HOLD'):
                    if signal == 'BUY' and portfolio.get_position(ticker) == 0:
                        # Calculate position size
                        quantity = self._calculate_position_size(
                            ticker, df, portfolio, signal
                        )
                        if quantity > 0:
                            orders.append((ticker, 'BUY', quantity))
                    
                    elif signal == 'SELL' and portfolio.get_position(ticker) > 0:
                        # Close position
                        quantity = portfolio.get_position(ticker)
                        orders.append((ticker, 'SELL', quantity))
                    
                    self.last_signals[ticker] = signal
                    
            except Exception as e:
                print(f"⚠ Agent error for {ticker}: {e}")
                continue
        
        return orders, self.current_logs
    
    def _calculate_position_size(
        self,
        ticker: str,
        market_data: pd.DataFrame,
        portfolio: Portfolio,
        signal: str
    ) -> int:
        """
        Calculate position size based on portfolio allocation.
        
        Args:
            ticker: Stock ticker
            market_data: Historical data for ticker
            portfolio: Current portfolio
            signal: Trade signal
            
        Returns:
            Number of shares to buy
        """
        if signal != 'BUY':
            return 0
        
        # Get current price
        current_price = market_data['close'].iloc[-1]
        
        # Fixed percentage allocation (10% of portfolio per position)
        allocation_pct = 0.10
        allocation_amount = portfolio.cash * allocation_pct
        
        # Calculate shares
        quantity = int(allocation_amount / current_price)
        
        return quantity


def create_agent_strategy(callback: Optional[Callable] = None) -> Callable:
    """
    Create a strategy function that uses the agent graph.
    
    Args:
        callback: Optional callback for agent events
        
    Returns:
        Strategy function compatible with BacktestEngine
    """
    strategy = AgentStrategy(callback=callback)
    
    def strategy_func(timestamp, market_data, portfolio):
        return strategy.generate_signals(timestamp, market_data, portfolio)
    
    return strategy_func
