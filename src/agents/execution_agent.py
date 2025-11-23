from typing import Dict, Any
from langchain_core.messages import AIMessage
from src.agents.base_agent import BaseAgent
from src.state import AgentState, TradeSignal
from src.data.db_client import TimescaleDBClient, DatabaseError


class ExecutionAgent(BaseAgent):
    """Execution Agent responsible for logging approved trades."""
    
    def __init__(self, model):
        super().__init__(
            name="ExecutionAgent",
            model=model,
            tools=[]
        )
        self.system_prompt = (
            "You are the Head Trader. You only execute if `risk_approval` is True. "
            "You log the trade details into the `execution_status` field."
        )
        
        # Initialize database client
        self.db_client = None
    
    def _ensure_db_connection(self):
        """Ensure database connection is established."""
        if self.db_client is None:
            try:
                self.db_client = TimescaleDBClient()
                self.db_client.connect()
            except DatabaseError as e:
                print(f"⚠ Database connection failed: {e}")
                self.db_client = None
    
    def run(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute approved trades and log to database.
        
        Only executes if risk_approval is True.
        """
        print(f"\n{'='*60}")
        print(f"🔴 {self.name} Starting")
        print(f"{'='*60}")
        
        # Check risk approval
        risk_approval = state.get("risk_approval", False)
        trade_signal = state.get("trade_signal", TradeSignal.HOLD)
        
        print(f"📋 Trade Signal: {trade_signal.value if hasattr(trade_signal, 'value') else trade_signal}")
        print(f"🔒 Risk Approval: {risk_approval}")
        
        # If not approved or HOLD, don't execute
        if not risk_approval or trade_signal == TradeSignal.HOLD or trade_signal == "HOLD":
            status = "NOT_EXECUTED - Risk not approved" if not risk_approval else "NOT_EXECUTED - Signal is HOLD"
            print(f"⏸️  {status}")
            return {
                "messages": [AIMessage(content=status)],
                "execution_status": status
            }
        
        # Extract trade details
        market_data = state.get("market_data", {})
        
        if isinstance(market_data, dict) or (hasattr(market_data, 'empty') and market_data.empty):
            status = "FAILED - No market data available"
            print(f"✗ {status}")
            return {
                "messages": [AIMessage(content=status)],
                "execution_status": status
            }
        
        ticker = market_data['symbol'].iloc[0] if 'symbol' in market_data.columns else 'UNKNOWN'
        current_price = market_data['close'].iloc[-1]
        sentiment_score = state.get("sentiment_score", 0.5)
        
        # Calculate quantity (simplified - use 10% of portfolio)
        quantity = 10  # Mock quantity for now
        
        # Determine side
        side = trade_signal.value if hasattr(trade_signal, 'value') else str(trade_signal)
        
        print(f"\n📊 Executing Trade:")
        print(f"  Symbol: {ticker}")
        print(f"  Side: {side}")
        print(f"  Quantity: {quantity}")
        print(f"  Price: ${current_price:.2f}")
        print(f"  Total Value: ${quantity * current_price:.2f}")
        
        # Log to database
        self._ensure_db_connection()
        
        if self.db_client:
            try:
                trade_id = self.db_client.log_trade(
                    symbol=ticker,
                    side=side,
                    quantity=quantity,
                    price=current_price,
                    status="EXECUTED",
                    sentiment_score=sentiment_score,
                    trade_signal=side,
                    risk_approved=True,
                    notes=f"Automated trade execution by Cortex5"
                )
                status = f"EXECUTED - Trade ID: {trade_id}"
                print(f"✅ {status}")
            except DatabaseError as e:
                status = f"LOGGED_LOCALLY - DB Error: {str(e)}"
                print(f"⚠ {status}")
        else:
            status = f"SIMULATED - {side} {quantity} {ticker} @ ${current_price:.2f} (DB not available)"
            print(f"⚠ {status}")
        
        return {
            "messages": [AIMessage(content=status)],
            "execution_status": status
        }
