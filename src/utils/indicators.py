"""Technical indicators for quantitative analysis."""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    RSI = 100 - (100 / (1 + RS))
    where RS = Average Gain / Average Loss over the period
    
    Args:
        prices: Series of closing prices
        period: Lookback period (default: 14)
        
    Returns:
        Series of RSI values (0-100)
    """
    # Calculate price changes
    delta = prices.diff()
    
    # Separate gains and losses
    gains = delta.where(delta > 0, 0.0)
    losses = -delta.where(delta < 0, 0.0)
    
    # Calculate average gains and losses
    avg_gains = gains.rolling(window=period, min_periods=period).mean()
    avg_losses = losses.rolling(window=period, min_periods=period).mean()
    
    # Calculate RS and RSI
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_macd(
    prices: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Dict[str, pd.Series]:
    """
    Calculate Moving Average Convergence Divergence (MACD).
    
    MACD Line = EMA(fast) - EMA(slow)
    Signal Line = EMA(MACD Line, signal_period)
    Histogram = MACD Line - Signal Line
    
    Args:
        prices: Series of closing prices
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line EMA period (default: 9)
        
    Returns:
        Dictionary with 'macd', 'signal', and 'histogram' Series
    """
    # Calculate EMAs
    ema_fast = prices.ewm(span=fast_period, adjust=False).mean()
    ema_slow = prices.ewm(span=slow_period, adjust=False).mean()
    
    # Calculate MACD line
    macd_line = ema_fast - ema_slow
    
    # Calculate signal line
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # Calculate histogram
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }


def calculate_bollinger_bands(
    prices: pd.Series,
    period: int = 20,
    num_std: float = 2.0
) -> Dict[str, pd.Series]:
    """
    Calculate Bollinger Bands.
    
    Middle Band = SMA(period)
    Upper Band = Middle Band + (num_std * Standard Deviation)
    Lower Band = Middle Band - (num_std * Standard Deviation)
    
    Args:
        prices: Series of closing prices
        period: Moving average period (default: 20)
        num_std: Number of standard deviations (default: 2.0)
        
    Returns:
        Dictionary with 'upper', 'middle', and 'lower' Series
    """
    # Calculate middle band (SMA)
    middle_band = prices.rolling(window=period).mean()
    
    # Calculate standard deviation
    std_dev = prices.rolling(window=period).std()
    
    # Calculate upper and lower bands
    upper_band = middle_band + (num_std * std_dev)
    lower_band = middle_band - (num_std * std_dev)
    
    return {
        'upper': upper_band,
        'middle': middle_band,
        'lower': lower_band
    }


def calculate_moving_average(
    prices: pd.Series,
    period: int,
    ma_type: str = 'sma'
) -> pd.Series:
    """
    Calculate Moving Average.
    
    Args:
        prices: Series of closing prices
        period: Moving average period
        ma_type: Type of MA - 'sma' (simple) or 'ema' (exponential)
        
    Returns:
        Series of moving average values
    """
    if ma_type.lower() == 'sma':
        return prices.rolling(window=period).mean()
    elif ma_type.lower() == 'ema':
        return prices.ewm(span=period, adjust=False).mean()
    else:
        raise ValueError(f"Invalid ma_type: {ma_type}. Use 'sma' or 'ema'")


def calculate_volatility(
    prices: pd.Series,
    period: int = 20,
    annualize: bool = False
) -> pd.Series:
    """
    Calculate historical volatility (standard deviation of returns).
    
    Args:
        prices: Series of closing prices
        period: Lookback period for volatility calculation
        annualize: If True, annualize the volatility (multiply by sqrt(252))
        
    Returns:
        Series of volatility values
    """
    # Calculate returns
    returns = prices.pct_change()
    
    # Calculate rolling standard deviation
    volatility = returns.rolling(window=period).std()
    
    # Annualize if requested
    if annualize:
        volatility = volatility * np.sqrt(252)  # 252 trading days per year
    
    return volatility


def detect_macd_crossover(macd_data: Dict[str, pd.Series]) -> Tuple[bool, bool]:
    """
    Detect MACD crossovers.
    
    Args:
        macd_data: Dictionary with 'macd' and 'signal' Series from calculate_macd()
        
    Returns:
        Tuple of (bullish_crossover, bearish_crossover)
        - bullish_crossover: True if MACD crossed above signal line
        - bearish_crossover: True if MACD crossed below signal line
    """
    macd = macd_data['macd']
    signal = macd_data['signal']
    
    # Get last two values
    if len(macd) < 2:
        return False, False
    
    macd_prev = macd.iloc[-2]
    macd_curr = macd.iloc[-1]
    signal_prev = signal.iloc[-2]
    signal_curr = signal.iloc[-1]
    
    # Detect crossovers
    bullish = (macd_prev <= signal_prev) and (macd_curr > signal_curr)
    bearish = (macd_prev >= signal_prev) and (macd_curr < signal_curr)
    
    return bullish, bearish


def calculate_support_resistance(
    prices: pd.Series,
    window: int = 20,
    num_levels: int = 3
) -> Dict[str, list]:
    """
    Calculate support and resistance levels using local minima/maxima.
    
    Args:
        prices: Series of closing prices
        window: Window size for finding local extrema
        num_levels: Number of support/resistance levels to return
        
    Returns:
        Dictionary with 'support' and 'resistance' lists
    """
    # Find local minima (support)
    local_min = prices.rolling(window=window, center=True).min()
    support_levels = prices[prices == local_min].unique()
    support_levels = sorted(support_levels)[:num_levels]
    
    # Find local maxima (resistance)
    local_max = prices.rolling(window=window, center=True).max()
    resistance_levels = prices[prices == local_max].unique()
    resistance_levels = sorted(resistance_levels, reverse=True)[:num_levels]
    
    return {
        'support': support_levels.tolist(),
        'resistance': resistance_levels.tolist()
    }


def calculate_atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14
) -> pd.Series:
    """
    Calculate Average True Range (ATR) - a measure of volatility.
    
    True Range = max(high - low, abs(high - prev_close), abs(low - prev_close))
    ATR = Moving Average of True Range
    
    Args:
        high: Series of high prices
        low: Series of low prices
        close: Series of closing prices
        period: ATR period (default: 14)
        
    Returns:
        Series of ATR values
    """
    # Calculate True Range
    prev_close = close.shift(1)
    
    tr1 = high - low
    tr2 = abs(high - prev_close)
    tr3 = abs(low - prev_close)
    
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Calculate ATR (using EMA)
    atr = true_range.ewm(span=period, adjust=False).mean()
    
    return atr
