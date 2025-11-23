"""Position sizing and risk management utilities for backtesting."""

from typing import Dict
import pandas as pd
import numpy as np

from src.backtesting.portfolio import Portfolio


class PositionSizer:
    """
    Calculate position sizes based on various allocation methods.
    """
    
    def __init__(self, method: str = 'fixed_pct', **kwargs):
        """
        Initialize position sizer.
        
        Args:
            method: Sizing method ('fixed_pct', 'kelly', 'equal_weight')
            **kwargs: Method-specific parameters
        """
        self.method = method
        self.params = kwargs
    
    def calculate_size(
        self,
        ticker: str,
        price: float,
        portfolio: Portfolio,
        signal_strength: float = 1.0
    ) -> int:
        """
        Calculate position size.
        
        Args:
            ticker: Stock ticker
            price: Current price
            portfolio: Portfolio state
            signal_strength: Signal confidence (0.0 to 1.0)
            
        Returns:
            Number of shares to buy
        """
        if self.method == 'fixed_pct':
            return self._fixed_percentage(ticker, price, portfolio, signal_strength)
        elif self.method == 'equal_weight':
            return self._equal_weight(ticker, price, portfolio)
        elif self.method == 'kelly':
            return self._kelly_criterion(ticker, price, portfolio, signal_strength)
        else:
            raise ValueError(f"Unknown sizing method: {self.method}")
    
    def _fixed_percentage(
        self,
        ticker: str,
        price: float,
        portfolio: Portfolio,
        signal_strength: float
    ) -> int:
        """Fixed percentage of portfolio per position."""
        pct = self.params.get('allocation_pct', 0.10)  # Default 10%
        allocation = portfolio.cash * pct * signal_strength
        return int(allocation / price)
    
    def _equal_weight(
        self,
        ticker: str,
        price: float,
        portfolio: Portfolio
    ) -> int:
        """Equal weight across all positions."""
        max_positions = self.params.get('max_positions', 10)
        current_positions = len(portfolio.positions)
        
        if current_positions >= max_positions:
            return 0
        
        allocation = portfolio.cash / (max_positions - current_positions)
        return int(allocation / price)
    
    def _kelly_criterion(
        self,
        ticker: str,
        price: float,
        portfolio: Portfolio,
        signal_strength: float
    ) -> int:
        """
        Kelly Criterion sizing (simplified).
        
        Kelly% = (Win% * Avg Win - Loss% * Avg Loss) / Avg Win
        """
        # Use conservative defaults if no history
        win_rate = self.params.get('win_rate', 0.55)
        avg_win = self.params.get('avg_win', 0.02)  # 2%
        avg_loss = self.params.get('avg_loss', 0.01)  # 1%
        
        kelly_pct = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        kelly_pct = max(0, min(kelly_pct, 0.25))  # Cap at 25%
        
        # Apply signal strength
        kelly_pct *= signal_strength
        
        allocation = portfolio.cash * kelly_pct
        return int(allocation / price)


def calculate_beta(
    strategy_returns: pd.Series,
    market_returns: pd.Series
) -> float:
    """
    Calculate beta (systematic risk) relative to market.
    
    Args:
        strategy_returns: Strategy returns series
        market_returns: Market (benchmark) returns series
        
    Returns:
        Beta coefficient
    """
    if len(strategy_returns) < 2 or len(market_returns) < 2:
        return 0.0
    
    # Align series
    aligned = pd.DataFrame({
        'strategy': strategy_returns,
        'market': market_returns
    }).dropna()
    
    if len(aligned) < 2:
        return 0.0
    
    # Calculate covariance and variance
    covariance = aligned['strategy'].cov(aligned['market'])
    market_variance = aligned['market'].var()
    
    if market_variance == 0:
        return 0.0
    
    beta = covariance / market_variance
    return beta


def calculate_correlation(
    strategy_returns: pd.Series,
    market_returns: pd.Series
) -> float:
    """
    Calculate correlation with market.
    
    Args:
        strategy_returns: Strategy returns series
        market_returns: Market returns series
        
    Returns:
        Correlation coefficient (-1 to 1)
    """
    if len(strategy_returns) < 2 or len(market_returns) < 2:
        return 0.0
    
    # Align series
    aligned = pd.DataFrame({
        'strategy': strategy_returns,
        'market': market_returns
    }).dropna()
    
    if len(aligned) < 2:
        return 0.0
    
    correlation = aligned['strategy'].corr(aligned['market'])
    return correlation if not np.isnan(correlation) else 0.0


def calculate_trade_analytics(trades: list) -> Dict:
    """
    Calculate detailed trade-level analytics.
    
    Args:
        trades: List of trade dictionaries
        
    Returns:
        Dictionary with trade analytics
    """
    if not trades:
        return {
            'avg_holding_period': 0,
            'trade_frequency': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'largest_win': 0,
            'largest_loss': 0
        }
    
    # Group trades by ticker to calculate holding periods
    buy_times = {}
    holding_periods = []
    wins = []
    losses = []
    
    for trade in trades:
        ticker = trade['ticker']
        
        if trade['side'] == 'BUY':
            buy_times[ticker] = trade['timestamp']
        elif trade['side'] == 'SELL' and ticker in buy_times:
            # Calculate holding period
            buy_time = buy_times[ticker]
            sell_time = trade['timestamp']
            
            if isinstance(buy_time, str):
                buy_time = pd.to_datetime(buy_time)
            if isinstance(sell_time, str):
                sell_time = pd.to_datetime(sell_time)
            
            holding_period = (sell_time - buy_time).total_seconds() / 86400  # Days
            holding_periods.append(holding_period)
            
            # Calculate P&L
            pnl = -trade['total_cost']  # Negative cost is profit
            if pnl > 0:
                wins.append(pnl)
            else:
                losses.append(abs(pnl))
            
            del buy_times[ticker]
    
    return {
        'avg_holding_period': np.mean(holding_periods) if holding_periods else 0,
        'trade_frequency': len([t for t in trades if t['side'] == 'SELL']),
        'avg_win': np.mean(wins) if wins else 0,
        'avg_loss': np.mean(losses) if losses else 0,
        'largest_win': max(wins) if wins else 0,
        'largest_loss': max(losses) if losses else 0,
    }
