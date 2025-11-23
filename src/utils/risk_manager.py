"""Risk management module for trade validation."""

import os
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from src.utils.indicators import calculate_volatility


class RiskManager:
    """Manages risk checks for trading decisions."""
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        max_position_pct: Optional[float] = None,
        max_volatility: Optional[float] = None,
        min_sentiment_score: Optional[float] = None
    ):
        """
        Initialize risk manager with portfolio constraints.
        
        Args:
            initial_capital: Starting capital in dollars
            max_position_pct: Maximum position size as % of portfolio (default: 0.10 = 10%)
            max_volatility: Maximum daily volatility threshold (default: 0.03 = 3%)
            min_sentiment_score: Minimum sentiment score for BUY signals (default: 0.5)
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # Load from env vars or use defaults
        self.max_position_pct = max_position_pct or float(os.getenv('MAX_POSITION_PCT', '0.10'))
        self.max_volatility = max_volatility or float(os.getenv('MAX_VOLATILITY', '0.03'))
        self.min_sentiment_score = min_sentiment_score or float(os.getenv('MIN_SENTIMENT_SCORE', '0.5'))
        
        # Portfolio state
        self.positions: Dict[str, Dict[str, Any]] = {}
    
    def check_position_size(
        self,
        signal: str,
        symbol: str,
        price: float,
        quantity: Optional[int] = None
    ) -> tuple[bool, str]:
        """
        Check if position size is within limits.
        
        Args:
            signal: Trade signal ('BUY', 'SELL', 'HOLD')
            symbol: Stock ticker
            price: Current price
            quantity: Number of shares (if None, calculates max allowed)
            
        Returns:
            Tuple of (approved: bool, reason: str)
        """
        if signal != 'BUY':
            return True, "Not a BUY signal"
        
        # Calculate max allowed position value
        max_position_value = self.current_capital * self.max_position_pct
        
        # Calculate proposed position value
        if quantity is None:
            quantity = int(max_position_value / price)
        
        position_value = quantity * price
        
        # Check if within limits
        if position_value > max_position_value:
            return False, (
                f"Position size ${position_value:,.2f} exceeds maximum "
                f"${max_position_value:,.2f} ({self.max_position_pct*100}% of portfolio)"
            )
        
        return True, f"Position size ${position_value:,.2f} is within limits"
    
    def check_volatility(
        self,
        market_data: pd.DataFrame,
        max_volatility: Optional[float] = None
    ) -> tuple[bool, str]:
        """
        Check if volatility is within acceptable range.
        
        Args:
            market_data: DataFrame with OHLCV data
            max_volatility: Override default max volatility
            
        Returns:
            Tuple of (approved: bool, reason: str)
        """
        if market_data.empty or len(market_data) < 20:
            return False, "Insufficient data to calculate volatility"
        
        max_vol = max_volatility or self.max_volatility
        
        # Calculate 20-day volatility
        volatility = calculate_volatility(market_data['close'], period=20)
        current_vol = volatility.iloc[-1]
        
        if pd.isna(current_vol):
            return False, "Unable to calculate volatility"
        
        if current_vol > max_vol:
            return False, (
                f"Volatility {current_vol:.4f} ({current_vol*100:.2f}%) exceeds "
                f"maximum {max_vol:.4f} ({max_vol*100:.2f}%)"
            )
        
        return True, f"Volatility {current_vol:.4f} ({current_vol*100:.2f}%) is acceptable"
    
    def check_sentiment_threshold(
        self,
        sentiment_score: float,
        signal: str
    ) -> tuple[bool, str]:
        """
        Check if sentiment meets threshold for the signal.
        
        Args:
            sentiment_score: Sentiment score (0.0-1.0)
            signal: Trade signal ('BUY', 'SELL', 'HOLD')
            
        Returns:
            Tuple of (approved: bool, reason: str)
        """
        # Only check sentiment for BUY signals
        if signal != 'BUY':
            return True, "Not a BUY signal"
        
        if sentiment_score < self.min_sentiment_score:
            return False, (
                f"Sentiment score {sentiment_score:.2f} below minimum "
                f"{self.min_sentiment_score:.2f} for BUY signals"
            )
        
        return True, f"Sentiment score {sentiment_score:.2f} meets threshold"
    
    def check_capital_availability(
        self,
        signal: str,
        price: float,
        quantity: int
    ) -> tuple[bool, str]:
        """
        Check if sufficient capital is available for the trade.
        
        Args:
            signal: Trade signal
            price: Stock price
            quantity: Number of shares
            
        Returns:
            Tuple of (approved: bool, reason: str)
        """
        if signal != 'BUY':
            return True, "Not a BUY signal"
        
        required_capital = price * quantity
        
        if required_capital > self.current_capital:
            return False, (
                f"Insufficient capital. Required: ${required_capital:,.2f}, "
                f"Available: ${self.current_capital:,.2f}"
            )
        
        return True, f"Sufficient capital available (${self.current_capital:,.2f})"
    
    def approve_trade(self, state: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Aggregate all risk checks and approve/reject trade.
        
        Args:
            state: Agent state dictionary with:
                - trade_signal: 'BUY', 'SELL', or 'HOLD'
                - market_data: DataFrame with OHLCV data
                - sentiment_score: float (0.0-1.0)
                
        Returns:
            Tuple of (approved: bool, reasons: list[str])
        """
        signal = state.get('trade_signal', 'HOLD')
        market_data = state.get('market_data', pd.DataFrame())
        sentiment_score = state.get('sentiment_score', 0.5)
        
        # If HOLD, no checks needed
        if signal == 'HOLD':
            return True, ["Signal is HOLD - no trade to approve"]
        
        reasons = []
        all_passed = True
        
        # Extract symbol and price from market data
        if market_data.empty:
            return False, ["No market data available for risk assessment"]
        
        symbol = market_data['symbol'].iloc[0] if 'symbol' in market_data.columns else 'UNKNOWN'
        current_price = market_data['close'].iloc[-1]
        
        # Calculate suggested quantity (max allowed by position size limit)
        max_position_value = self.current_capital * self.max_position_pct
        suggested_quantity = int(max_position_value / current_price)
        
        # Check 1: Position size
        passed, reason = self.check_position_size(signal, symbol, current_price, suggested_quantity)
        reasons.append(f"✓ {reason}" if passed else f"✗ {reason}")
        all_passed = all_passed and passed
        
        # Check 2: Volatility
        passed, reason = self.check_volatility(market_data)
        reasons.append(f"✓ {reason}" if passed else f"✗ {reason}")
        all_passed = all_passed and passed
        
        # Check 3: Sentiment threshold
        passed, reason = self.check_sentiment_threshold(sentiment_score, signal)
        reasons.append(f"✓ {reason}" if passed else f"✗ {reason}")
        all_passed = all_passed and passed
        
        # Check 4: Capital availability
        passed, reason = self.check_capital_availability(signal, current_price, suggested_quantity)
        reasons.append(f"✓ {reason}" if passed else f"✗ {reason}")
        all_passed = all_passed and passed
        
        return all_passed, reasons
    
    def update_position(
        self,
        symbol: str,
        side: str,
        quantity: int,
        price: float
    ) -> None:
        """
        Update portfolio state after trade execution.
        
        Args:
            symbol: Stock ticker
            side: 'BUY' or 'SELL'
            quantity: Number of shares
            price: Execution price
        """
        if side == 'BUY':
            # Deduct capital
            self.current_capital -= quantity * price
            
            # Update position
            if symbol in self.positions:
                self.positions[symbol]['quantity'] += quantity
            else:
                self.positions[symbol] = {'quantity': quantity, 'avg_price': price}
                
        elif side == 'SELL':
            # Add capital
            self.current_capital += quantity * price
            
            # Update position
            if symbol in self.positions:
                self.positions[symbol]['quantity'] -= quantity
                if self.positions[symbol]['quantity'] <= 0:
                    del self.positions[symbol]
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get current portfolio summary."""
        return {
            'cash': self.current_capital,
            'positions': self.positions,
            'total_value': self.current_capital  # TODO: Add position values
        }
