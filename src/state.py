from typing import TypedDict, Annotated, List, Dict, Any
from enum import Enum
import operator
from langchain_core.messages import BaseMessage

class TradeSignal(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    market_data: Any
    sentiment_score: float
    trade_signal: TradeSignal
    risk_approval: bool
    execution_status: str
