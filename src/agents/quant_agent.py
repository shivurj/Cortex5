from typing import Dict, Any
import pandas as pd
from langchain_core.messages import AIMessage
from src.agents.base_agent import BaseAgent
from src.state import AgentState, TradeSignal
from src.utils.indicators import calculate_rsi, calculate_macd, detect_macd_crossover


class QuantAgent(BaseAgent):
    """Quant Agent responsible for technical analysis and trade signal generation."""
    
    def __init__(self, model, callback=None):
        super().__init__(
            name="QuantAgent",
            model=model,
            tools=[],
            callback=callback
        )
        self.system_prompt = (
            "You are the Quant Researcher. You analyze the `market_data` provided by the Data Agent "
            "and the `sentiment_score` from the Sentiment Agent. You output a `trade_signal` (BUY/SELL/HOLD) "
            "based on technical indicators like RSI and MACD."
        )
    
    def run(self, state: AgentState) -> Dict[str, Any]:
        """
        Perform technical analysis and generate trade signal.
        
        Uses RSI and MACD indicators to determine BUY/SELL/HOLD signals.
        """
        self.log("Starting technical analysis...", "status")
        
        # Get market data
        market_data = state.get("market_data", {})
        
        if isinstance(market_data, dict) or (hasattr(market_data, 'empty') and market_data.empty):
            print("✗ No market data available for analysis")
            return {
                "messages": [AIMessage(content="No market data available for technical analysis")],
                "trade_signal": TradeSignal.HOLD
            }
        
        # Extract ticker
        ticker = market_data['symbol'].iloc[0] if 'symbol' in market_data.columns else 'UNKNOWN'
        self.log(f"Analyzing: {ticker}", "info")
        
        # Ensure we have enough data
        if len(market_data) < 26:  # Need at least 26 periods for MACD
            print(f"⚠ Insufficient data ({len(market_data)} rows), need at least 26")
            return {
                "messages": [AIMessage(content=f"Insufficient data for technical analysis ({len(market_data)} rows)")],
                "trade_signal": TradeSignal.HOLD
            }
        
        # Calculate technical indicators
        self.log("Calculating technical indicators...", "status")
        
        prices = market_data['close']
        
        # Calculate RSI
        rsi = calculate_rsi(prices, period=14)
        current_rsi = rsi.iloc[-1]
        
        # Calculate MACD
        macd_data = calculate_macd(prices)
        current_macd = macd_data['macd'].iloc[-1]
        current_signal = macd_data['signal'].iloc[-1]
        current_histogram = macd_data['histogram'].iloc[-1]
        
        # Detect crossovers
        bullish_cross, bearish_cross = detect_macd_crossover(macd_data)
        
        print(f"  RSI: {current_rsi:.2f}")
        print(f"  MACD: {current_macd:.4f}")
        print(f"  Signal: {current_signal:.4f}")
        print(f"  Histogram: {current_histogram:.4f}")
        print(f"  Bullish Crossover: {bullish_cross}")
        print(f"  Bearish Crossover: {bearish_cross}")
        
        # Get sentiment score
        sentiment_score = state.get("sentiment_score", 0.5)
        self.log(f"Sentiment Score: {sentiment_score:.2f}", "info")
        
        # Trading strategy logic
        signal = TradeSignal.HOLD
        reasoning = []
        
        # Adjust thresholds based on sentiment
        # Bullish sentiment -> Relax buy thresholds, tighten sell thresholds
        # Bearish sentiment -> Tighten buy thresholds, relax sell thresholds
        buy_rsi_threshold = 30
        sell_rsi_threshold = 70
        
        if sentiment_score > 0.6:
            buy_rsi_threshold = 40  # Easier to buy
            sell_rsi_threshold = 80 # Harder to sell
            reasoning.append(f"Bullish sentiment ({sentiment_score:.2f}) -> Adjusted thresholds")
        elif sentiment_score < 0.4:
            buy_rsi_threshold = 20  # Harder to buy
            sell_rsi_threshold = 60 # Easier to sell
            reasoning.append(f"Bearish sentiment ({sentiment_score:.2f}) -> Adjusted thresholds")
        
        # BUY conditions
        if current_rsi < buy_rsi_threshold:
            reasoning.append(f"RSI is oversold ({current_rsi:.2f} < {buy_rsi_threshold})")
            if bullish_cross:
                signal = TradeSignal.BUY
                reasoning.append("MACD bullish crossover detected")
            elif current_macd > current_signal:
                signal = TradeSignal.BUY
                reasoning.append("MACD above signal line")
        elif buy_rsi_threshold <= current_rsi <= 50 and bullish_cross:
            signal = TradeSignal.BUY
            reasoning.append(f"RSI in neutral zone ({current_rsi:.2f})")
            reasoning.append("MACD bullish crossover detected")
        
        # SELL conditions
        elif current_rsi > sell_rsi_threshold:
            reasoning.append(f"RSI is overbought ({current_rsi:.2f} > {sell_rsi_threshold})")
            if bearish_cross:
                signal = TradeSignal.SELL
                reasoning.append("MACD bearish crossover detected")
            elif current_macd < current_signal:
                signal = TradeSignal.SELL
                reasoning.append("MACD below signal line")
        elif 50 <= current_rsi <= sell_rsi_threshold and bearish_cross:
            signal = TradeSignal.SELL
            reasoning.append(f"RSI in neutral-high zone ({current_rsi:.2f})")
            reasoning.append("MACD bearish crossover detected")
        
        # HOLD conditions
        else:
            reasoning.append(f"RSI in neutral zone ({current_rsi:.2f})")
            reasoning.append("No strong MACD signal")
        
        # Compile reasoning
        reasoning_text = " | ".join(reasoning)
        
        self.log(f"Signal: {signal.value} | {reasoning_text}", "success", {"signal": signal.value, "rsi": current_rsi, "macd": current_macd})
        
        return {
            "messages": [AIMessage(content=f"Technical Analysis for {ticker}: {signal.value}. {reasoning_text}")],
            "trade_signal": signal
        }
