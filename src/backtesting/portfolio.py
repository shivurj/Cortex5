"""Portfolio management for backtesting.

Tracks cash balance, positions, and trade history with transaction costs.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderSide(Enum):
    """Order side enumeration."""
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Trade:
    """Represents a single trade execution."""
    timestamp: datetime
    ticker: str
    side: OrderSide
    quantity: int
    price: float
    commission: float
    slippage: float
    total_cost: float  # Including commission and slippage
    
    def __repr__(self) -> str:
        return (f"Trade({self.timestamp.strftime('%Y-%m-%d %H:%M')}, "
                f"{self.ticker}, {self.side.value}, {self.quantity} @ ${self.price:.2f})")


class InsufficientFundsError(Exception):
    """Raised when attempting to trade without sufficient capital."""
    pass


class InsufficientSharesError(Exception):
    """Raised when attempting to sell more shares than owned."""
    pass


class Portfolio:
    """
    Portfolio manager for backtesting.
    
    Tracks cash balance, positions, and maintains trade history.
    Applies transaction costs (commission and slippage) to all trades.
    """
    
    def __init__(
        self,
        initial_capital: float,
        commission_pct: float = 0.001,  # 0.1% commission
        slippage_pct: float = 0.0005     # 0.05% slippage
    ):
        """
        Initialize portfolio.
        
        Args:
            initial_capital: Starting cash balance
            commission_pct: Commission as percentage of trade value (e.g., 0.001 = 0.1%)
            slippage_pct: Slippage as percentage of price (e.g., 0.0005 = 0.05%)
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct
        
        # Positions: ticker -> quantity
        self.positions: Dict[str, int] = {}
        
        # Trade history
        self.trades: List[Trade] = []
        
        # Equity history for performance tracking
        self.equity_history: List[tuple[datetime, float]] = []
    
    def buy(
        self,
        ticker: str,
        quantity: int,
        price: float,
        timestamp: datetime
    ) -> Trade:
        """
        Execute a buy order.
        
        Args:
            ticker: Stock ticker symbol
            quantity: Number of shares to buy
            price: Market price per share
            timestamp: Execution timestamp
            
        Returns:
            Trade object representing the execution
            
        Raises:
            InsufficientFundsError: If not enough cash to complete purchase
        """
        # Calculate costs
        slippage = price * self.slippage_pct  # Buy at slightly higher price
        effective_price = price + slippage
        gross_cost = quantity * effective_price
        commission = gross_cost * self.commission_pct
        total_cost = gross_cost + commission
        
        # Check if we have enough cash
        if total_cost > self.cash:
            raise InsufficientFundsError(
                f"Insufficient funds to buy {quantity} {ticker}. "
                f"Required: ${total_cost:.2f}, Available: ${self.cash:.2f}"
            )
        
        # Execute trade
        self.cash -= total_cost
        self.positions[ticker] = self.positions.get(ticker, 0) + quantity
        
        # Record trade
        trade = Trade(
            timestamp=timestamp,
            ticker=ticker,
            side=OrderSide.BUY,
            quantity=quantity,
            price=price,
            commission=commission,
            slippage=slippage * quantity,
            total_cost=total_cost
        )
        self.trades.append(trade)
        
        return trade
    
    def sell(
        self,
        ticker: str,
        quantity: int,
        price: float,
        timestamp: datetime
    ) -> Trade:
        """
        Execute a sell order.
        
        Args:
            ticker: Stock ticker symbol
            quantity: Number of shares to sell
            price: Market price per share
            timestamp: Execution timestamp
            
        Returns:
            Trade object representing the execution
            
        Raises:
            InsufficientSharesError: If trying to sell more shares than owned
        """
        # Check if we have enough shares
        current_position = self.positions.get(ticker, 0)
        if quantity > current_position:
            raise InsufficientSharesError(
                f"Insufficient shares to sell {quantity} {ticker}. "
                f"Current position: {current_position}"
            )
        
        # Calculate proceeds
        slippage = price * self.slippage_pct  # Sell at slightly lower price
        effective_price = price - slippage
        gross_proceeds = quantity * effective_price
        commission = gross_proceeds * self.commission_pct
        net_proceeds = gross_proceeds - commission
        
        # Execute trade
        self.cash += net_proceeds
        self.positions[ticker] -= quantity
        
        # Remove position if fully closed
        if self.positions[ticker] == 0:
            del self.positions[ticker]
        
        # Record trade
        trade = Trade(
            timestamp=timestamp,
            ticker=ticker,
            side=OrderSide.SELL,
            quantity=quantity,
            price=price,
            commission=commission,
            slippage=slippage * quantity,
            total_cost=-net_proceeds  # Negative because it's proceeds
        )
        self.trades.append(trade)
        
        return trade
    
    def get_position(self, ticker: str) -> int:
        """Get current position size for a ticker."""
        return self.positions.get(ticker, 0)
    
    def get_equity(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio equity.
        
        Args:
            current_prices: Dictionary mapping tickers to current prices
            
        Returns:
            Total equity (cash + position values)
        """
        position_value = sum(
            qty * current_prices.get(ticker, 0)
            for ticker, qty in self.positions.items()
        )
        return self.cash + position_value
    
    def record_equity(self, timestamp: datetime, current_prices: Dict[str, float]):
        """Record equity at a point in time for performance tracking."""
        equity = self.get_equity(current_prices)
        self.equity_history.append((timestamp, equity))
    
    def get_trade_history(self) -> List[Trade]:
        """Get complete trade history."""
        return self.trades.copy()
    
    def get_summary(self) -> Dict:
        """Get portfolio summary statistics."""
        return {
            'initial_capital': self.initial_capital,
            'current_cash': self.cash,
            'positions': dict(self.positions),
            'total_trades': len(self.trades),
            'buy_trades': sum(1 for t in self.trades if t.side == OrderSide.BUY),
            'sell_trades': sum(1 for t in self.trades if t.side == OrderSide.SELL),
            'total_commission_paid': sum(t.commission for t in self.trades),
        }
    
    def __repr__(self) -> str:
        return (f"Portfolio(cash=${self.cash:.2f}, "
                f"positions={len(self.positions)}, "
                f"trades={len(self.trades)})")
