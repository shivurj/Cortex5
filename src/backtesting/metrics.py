"""Performance metrics calculation for backtesting results.

Calculates standard financial metrics including returns, risk-adjusted returns,
drawdowns, and trade-level statistics.
"""

from typing import Dict, List
import pandas as pd
import numpy as np


def calculate_returns(equity_curve: pd.Series) -> Dict[str, float]:
    """
    Calculate return metrics from equity curve.
    
    Args:
        equity_curve: Series of equity values over time
        
    Returns:
        Dictionary with total_return and CAGR
    """
    if len(equity_curve) < 2:
        return {'total_return': 0.0, 'cagr': 0.0}
    
    initial_equity = equity_curve.iloc[0]
    final_equity = equity_curve.iloc[-1]
    
    total_return = (final_equity / initial_equity) - 1
    
    # Calculate CAGR (Compound Annual Growth Rate)
    # Assuming equity_curve index is datetime
    if isinstance(equity_curve.index, pd.DatetimeIndex):
        years = (equity_curve.index[-1] - equity_curve.index[0]).days / 365.25
        if years > 0:
            cagr = (final_equity / initial_equity) ** (1 / years) - 1
        else:
            cagr = 0.0
    else:
        # If no datetime index, assume daily data
        days = len(equity_curve)
        years = days / 252  # 252 trading days per year
        if years > 0:
            cagr = (final_equity / initial_equity) ** (1 / years) - 1
        else:
            cagr = 0.0
    
    return {
        'total_return': total_return,
        'cagr': cagr
    }


def calculate_volatility(returns: pd.Series, annualize: bool = True) -> float:
    """
    Calculate volatility (standard deviation of returns).
    
    Args:
        returns: Series of period returns
        annualize: Whether to annualize the volatility
        
    Returns:
        Annualized volatility
    """
    if len(returns) < 2:
        return 0.0
    
    vol = returns.std()
    
    if annualize:
        # Assume daily returns, annualize with sqrt(252)
        vol = vol * np.sqrt(252)
    
    return vol


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02,
    annualize: bool = True
) -> float:
    """
    Calculate Sharpe ratio (risk-adjusted return).
    
    Args:
        returns: Series of period returns
        risk_free_rate: Annual risk-free rate (default 2%)
        annualize: Whether to annualize the ratio
        
    Returns:
        Sharpe ratio
    """
    if len(returns) < 2:
        return 0.0
    
    excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
    
    if excess_returns.std() == 0:
        return 0.0
    
    sharpe = excess_returns.mean() / excess_returns.std()
    
    if annualize:
        sharpe = sharpe * np.sqrt(252)
    
    return sharpe


def calculate_sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02,
    annualize: bool = True
) -> float:
    """
    Calculate Sortino ratio (downside risk-adjusted return).
    
    Only considers downside volatility (negative returns).
    
    Args:
        returns: Series of period returns
        risk_free_rate: Annual risk-free rate
        annualize: Whether to annualize the ratio
        
    Returns:
        Sortino ratio
    """
    if len(returns) < 2:
        return 0.0
    
    excess_returns = returns - (risk_free_rate / 252)
    
    # Calculate downside deviation (only negative returns)
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0.0
    
    downside_std = downside_returns.std()
    sortino = excess_returns.mean() / downside_std
    
    if annualize:
        sortino = sortino * np.sqrt(252)
    
    return sortino


def calculate_max_drawdown(equity_curve: pd.Series) -> Dict[str, float]:
    """
    Calculate maximum drawdown and related metrics.
    
    Args:
        equity_curve: Series of equity values over time
        
    Returns:
        Dictionary with max_drawdown (as percentage) and max_drawdown_duration (days)
    """
    if len(equity_curve) < 2:
        return {'max_drawdown': 0.0, 'max_drawdown_duration': 0}
    
    # Calculate running maximum
    running_max = equity_curve.expanding().max()
    
    # Calculate drawdown at each point
    drawdown = (equity_curve - running_max) / running_max
    
    max_dd = drawdown.min()
    
    # Calculate drawdown duration
    # Find periods where we're in drawdown
    in_drawdown = drawdown < 0
    
    if not in_drawdown.any():
        max_dd_duration = 0
    else:
        # Find longest consecutive drawdown period
        drawdown_periods = []
        current_period = 0
        
        for is_dd in in_drawdown:
            if is_dd:
                current_period += 1
            else:
                if current_period > 0:
                    drawdown_periods.append(current_period)
                current_period = 0
        
        if current_period > 0:
            drawdown_periods.append(current_period)
        
        max_dd_duration = max(drawdown_periods) if drawdown_periods else 0
    
    return {
        'max_drawdown': abs(max_dd),
        'max_drawdown_duration': max_dd_duration
    }


def calculate_win_rate(trades: List[Dict]) -> float:
    """
    Calculate win rate (percentage of profitable trades).
    
    Args:
        trades: List of trade dictionaries
        
    Returns:
        Win rate as decimal (0.0 to 1.0)
    """
    if not trades:
        return 0.0
    
    # Group trades into round trips (buy + sell)
    # For simplicity, calculate P&L per trade
    profitable_trades = 0
    total_closed_trades = 0
    
    for trade in trades:
        if trade['side'] == 'SELL':
            # Selling is closing a position, count as a trade
            total_closed_trades += 1
            # If total_cost is negative (proceeds), it's profitable
            if trade['total_cost'] < 0:  # Negative cost means we received money
                profitable_trades += 1
    
    if total_closed_trades == 0:
        return 0.0
    
    return profitable_trades / total_closed_trades


def calculate_profit_factor(trades: List[Dict]) -> float:
    """
    Calculate profit factor (gross profit / gross loss).
    
    Args:
        trades: List of trade dictionaries
        
    Returns:
        Profit factor
    """
    if not trades:
        return 0.0
    
    gross_profit = 0.0
    gross_loss = 0.0
    
    for trade in trades:
        if trade['side'] == 'SELL':
            pnl = -trade['total_cost']  # Negative cost is profit
            if pnl > 0:
                gross_profit += pnl
            else:
                gross_loss += abs(pnl)
    
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0
    
    return gross_profit / gross_loss


def calculate_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """
    Calculate Value at Risk (VaR) using historical method.
    
    Args:
        returns: Series of period returns
        confidence: Confidence level (e.g., 0.95 for 95%)
        
    Returns:
        VaR as a positive number (e.g., 0.02 means 2% loss)
    """
    if len(returns) < 2:
        return 0.0
    
    # Historical VaR is simply the percentile
    var = -returns.quantile(1 - confidence)
    
    return max(0, var)


def calculate_cvar(returns: pd.Series, confidence: float = 0.95) -> float:
    """
    Calculate Conditional Value at Risk (CVaR / Expected Shortfall).
    
    Average loss beyond the VaR threshold.
    
    Args:
        returns: Series of period returns
        confidence: Confidence level
        
    Returns:
        CVaR as a positive number
    """
    if len(returns) < 2:
        return 0.0
    
    var = calculate_var(returns, confidence)
    
    # CVaR is the average of returns worse than VaR
    worst_returns = returns[returns <= -var]
    
    if len(worst_returns) == 0:
        return var
    
    cvar = -worst_returns.mean()
    
    return max(0, cvar)


def calculate_all_metrics(
    equity_curve: pd.DataFrame,
    trades: List[Dict],
    risk_free_rate: float = 0.02
) -> Dict:
    """
    Calculate all performance metrics.
    
    Args:
        equity_curve: DataFrame with 'timestamp' and 'equity' columns
        trades: List of trade dictionaries
        risk_free_rate: Annual risk-free rate
        
    Returns:
        Dictionary with all metrics
    """
    if equity_curve.empty:
        return {}
    
    # Set timestamp as index
    equity_series = equity_curve.set_index('timestamp')['equity']
    
    # Calculate returns
    returns = equity_series.pct_change().dropna()
    
    # Calculate all metrics
    return_metrics = calculate_returns(equity_series)
    volatility = calculate_volatility(returns)
    sharpe = calculate_sharpe_ratio(returns, risk_free_rate)
    sortino = calculate_sortino_ratio(returns, risk_free_rate)
    dd_metrics = calculate_max_drawdown(equity_series)
    win_rate = calculate_win_rate(trades)
    profit_factor = calculate_profit_factor(trades)
    var_95 = calculate_var(returns, 0.95)
    cvar_95 = calculate_cvar(returns, 0.95)
    
    return {
        **return_metrics,
        'volatility': volatility,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        **dd_metrics,
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'var_95': var_95,
        'cvar_95': cvar_95,
        'total_trades': len([t for t in trades if t['side'] == 'SELL']),
    }


def match_trades(trades: List[Dict]) -> List[Dict]:
    """
    Match buy and sell trades to calculate P&L (FIFO).
    
    Args:
        trades: List of raw trade dictionaries
        
    Returns:
        List of round-trip trades with P&L
    """
    if not trades:
        return []
    
    # Group by ticker
    trades_by_ticker = {}
    for trade in trades:
        ticker = trade['ticker']
        if ticker not in trades_by_ticker:
            trades_by_ticker[ticker] = []
        trades_by_ticker[ticker].append(trade)
    
    matched_trades = []
    
    for ticker, ticker_trades in trades_by_ticker.items():
        # FIFO queue of open buy positions: (quantity, price, timestamp, commission)
        open_positions = []
        
        for trade in ticker_trades:
            if trade['side'] == 'BUY':
                open_positions.append({
                    'quantity': trade['quantity'],
                    'price': trade['price'],
                    'timestamp': trade['timestamp'],
                    'commission': trade['commission']
                })
            
            elif trade['side'] == 'SELL':
                qty_to_close = trade['quantity']
                sell_price = trade['price']
                sell_timestamp = trade['timestamp']
                sell_commission = trade['commission']
                
                # Calculate weighted average entry price
                total_entry_cost = 0
                total_entry_qty = 0
                entry_timestamps = []
                entry_commissions = 0
                
                while qty_to_close > 0 and open_positions:
                    position = open_positions[0]
                    
                    if position['quantity'] <= qty_to_close:
                        # Fully close this position
                        matched_qty = position['quantity']
                        open_positions.pop(0)
                    else:
                        # Partially close
                        matched_qty = qty_to_close
                        position['quantity'] -= matched_qty
                    
                    total_entry_cost += matched_qty * position['price']
                    total_entry_qty += matched_qty
                    entry_timestamps.append(position['timestamp'])
                    
                    # Pro-rate commission
                    entry_commissions += position['commission'] * (matched_qty / (matched_qty + position['quantity'] if position in open_positions else matched_qty))
                    
                    qty_to_close -= matched_qty
                
                if total_entry_qty > 0:
                    avg_entry_price = total_entry_cost / total_entry_qty
                    gross_pnl = (sell_price - avg_entry_price) * total_entry_qty
                    net_pnl = gross_pnl - sell_commission - entry_commissions
                    pnl_pct = (net_pnl / total_entry_cost) * 100
                    
                    matched_trades.append({
                        'ticker': ticker,
                        'entry_date': min(entry_timestamps),
                        'exit_date': sell_timestamp,
                        'entry_price': avg_entry_price,
                        'exit_price': sell_price,
                        'quantity': total_entry_qty,
                        'pnl': net_pnl,
                        'pnl_pct': pnl_pct,
                        'side': 'LONG' # Currently only supporting long
                    })
    
    # Sort by exit date
    matched_trades.sort(key=lambda x: x['exit_date'], reverse=True)
    
    return matched_trades
