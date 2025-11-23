"""Simple test script to verify backtesting engine works.

Tests the Portfolio and BacktestEngine with a basic buy-and-hold strategy.
"""

import sys
sys.path.insert(0, '/Volumes/Dhitva/Bots/Interview_Prep/Cortex5')

from datetime import datetime, timedelta
from src.backtesting.engine import BacktestEngine
from src.backtesting.metrics import calculate_all_metrics


def simple_buy_and_hold_strategy(timestamp, market_data, portfolio):
    """
    Simple buy-and-hold strategy for testing.
    
    Buys on first day, holds until end.
    """
    orders = []
    
    # Only trade if we have data
    if not market_data:
        return orders
    
    # Get first ticker
    ticker = list(market_data.keys())[0]
    df = market_data[ticker]
    
    if len(df) < 2:
        return orders
    
    # Buy on first bar if we don't have a position
    if portfolio.get_position(ticker) == 0:
        # Use 90% of capital
        price = df['close'].iloc[-1]
        quantity = int((portfolio.cash * 0.9) / price)
        
        if quantity > 0:
            orders.append((ticker, 'BUY', quantity))
    
    return orders


def main():
    print("="*60)
    print("BACKTESTING ENGINE TEST")
    print("="*60)
    
    # Initialize engine
    engine = BacktestEngine(
        initial_capital=100000.0,
        commission_pct=0.001,
        slippage_pct=0.0005
    )
    
    # Load historical data (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"\nLoading data for AAPL...")
    engine.load_historical_data(
        tickers=['AAPL'],
        start_date=start_date,
        end_date=end_date,
        interval='1d'
    )
    
    # Run backtest
    print(f"\nRunning backtest with buy-and-hold strategy...")
    results = engine.run(simple_buy_and_hold_strategy)
    
    # Calculate metrics
    print(f"\nCalculating performance metrics...")
    metrics = calculate_all_metrics(
        equity_curve=results['equity_curve'],
        trades=results['trades']
    )
    
    # Display results
    print(f"\n{'='*60}")
    print("PERFORMANCE METRICS")
    print(f"{'='*60}")
    print(f"Total Return:     {metrics.get('total_return', 0)*100:.2f}%")
    print(f"CAGR:             {metrics.get('cagr', 0)*100:.2f}%")
    print(f"Sharpe Ratio:     {metrics.get('sharpe_ratio', 0):.2f}")
    print(f"Sortino Ratio:    {metrics.get('sortino_ratio', 0):.2f}")
    print(f"Max Drawdown:     {metrics.get('max_drawdown', 0)*100:.2f}%")
    print(f"Volatility:       {metrics.get('volatility', 0)*100:.2f}%")
    print(f"Win Rate:         {metrics.get('win_rate', 0)*100:.2f}%")
    print(f"Profit Factor:    {metrics.get('profit_factor', 0):.2f}")
    print(f"Total Trades:     {metrics.get('total_trades', 0)}")
    print(f"{'='*60}")
    
    print(f"\n✅ Backtesting engine test complete!")


if __name__ == "__main__":
    main()
