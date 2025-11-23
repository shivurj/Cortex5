from typing import Dict, Any
from langchain_core.messages import AIMessage
from src.agents.base_agent import BaseAgent
from src.state import AgentState, TradeSignal
from src.utils.risk_manager import RiskManager


class RiskAgent(BaseAgent):
    """Risk Agent responsible for validating trades against risk parameters."""
    
    def __init__(self, model, callback=None):
        super().__init__(
            name="RiskAgent",
            model=model,
            tools=[],
            callback=callback
        )
        self.system_prompt = (
            "You are the Risk Manager. You are the gatekeeper. You review the `trade_signal`. "
            "If the signal is BUY, check if we have enough capital. If the volatility is too high, "
            "set `risk_approval` to False. You are conservative and paranoid."
        )
        
        # Initialize risk manager
        self.risk_manager = RiskManager()
    
    def run(self, state: AgentState) -> Dict[str, Any]:
        """
        Validate trade against risk parameters.
        
        Checks position size, volatility, sentiment, and capital availability.
        """
        self.log("Starting risk assessment...", "status")
        
        # Get trade signal
        trade_signal = state.get("trade_signal", TradeSignal.HOLD)
        
        self.log(f"Trade Signal: {trade_signal.value if hasattr(trade_signal, 'value') else trade_signal}", "info")
        
        # If HOLD, no risk checks needed
        if trade_signal == TradeSignal.HOLD or trade_signal == "HOLD":
            print("✓ Signal is HOLD - no risk checks required")
            return {
                "messages": [AIMessage(content="No trade to approve (signal is HOLD)")],
                "risk_approval": True
            }
        
        # Perform risk checks
        self.log("Performing risk checks...", "status")
        approved, reasons = self.risk_manager.approve_trade(state)
        
        # Print results
        print(f"\n{'='*60}")
        print(f"Risk Assessment Results:")
        print(f"{'='*60}")
        for reason in reasons:
            print(f"  {reason}")
        print(f"{'='*60}")
        
        if approved:
            self.log(f"Trade APPROVED: {' | '.join(reasons)}", "success")
        else:
            self.log(f"Trade REJECTED: {' | '.join(reasons)}", "error")
        
        # Compile message
        status = "APPROVED" if approved else "REJECTED"
        message = f"Risk Assessment: {status}\n" + "\n".join(reasons)
        
        return {
            "messages": [AIMessage(content=message)],
            "risk_approval": approved
        }
