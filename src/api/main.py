from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncio
import json
from datetime import datetime
from langchain_core.messages import HumanMessage

from src.api.websocket_manager import manager
from src.data.db_client import TimescaleDBClient
from src.data.stock_universe import get_all_stocks
from src.graph import create_graph
from src.backtesting.engine import BacktestEngine
from src.backtesting.metrics import calculate_all_metrics
from pydantic import BaseModel

app = FastAPI(title="Cortex5 API", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Client
db = TimescaleDBClient()

@app.on_event("startup")
def startup_db():
    try:
        db.connect()
    except Exception as e:
        print(f"Failed to connect to DB on startup: {e}")

@app.on_event("shutdown")
def shutdown_db():
    db.close()

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/trades")
async def get_trades(limit: int = 50):
    # TODO: Implement get_trades in TimescaleDBClient
    # For now, return empty list or mock
    try:
        # We will add this method to db_client shortly
        if hasattr(db, 'get_trades'):
            return db.get_trades(limit=limit)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio")
async def get_portfolio():
    try:
        value = db.get_portfolio_value()
        # Mocking cash and positions for now as we don't have a full portfolio table yet
        return {
            "total_value": value,
            "cash": 100000.0, # Placeholder
            "positions": []   # Placeholder
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-data/{ticker}")
async def get_market_data(ticker: str, limit: int = 100):
    try:
        df = db.query_market_data(ticker, limit=limit)
        if df.empty:
            return []
        # Convert to list of dicts for JSON response
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stocks")
async def get_stocks():
    """Get list of available stocks for analysis."""
    try:
        return get_all_stocks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_agent_analysis(ticker: str):
    """
    Background task to run the agent graph and stream updates.
    """
    await manager.broadcast({
        "type": "status", 
        "agent": "System", 
        "message": f"Starting analysis for {ticker}...",
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        loop = asyncio.get_running_loop()
        
        def sync_callback(payload):
            asyncio.run_coroutine_threadsafe(manager.broadcast(payload), loop)

        # Create the graph
        graph = create_graph(callback=sync_callback)
        
        # Initial state
        initial_state = {
            "messages": [HumanMessage(content=f"Analyze {ticker}")],
            "data": {"ticker": ticker}
        }
        
        # Run the graph
        # We run in a separate thread to avoid blocking the event loop
        result = await asyncio.to_thread(graph.invoke, initial_state)
        
        # Extract serializable data from result
        result_data = {
            "trade_signal": str(result.get("trade_signal", "UNKNOWN")),
            "sentiment_score": result.get("sentiment_score"),
            "risk_approval": result.get("risk_approval"),
            "execution_status": result.get("execution_status")
        }
        
        await manager.broadcast({
            "type": "result",
            "agent": "ExecutionAgent",
            "data": result_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        await manager.broadcast({
            "type": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "analyze":
                ticker = data.get("ticker")
                # Run analysis in background
                asyncio.create_task(run_agent_analysis(ticker))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Backtest request model
class BacktestRequest(BaseModel):
    tickers: List[str]
    start_date: str  # ISO format
    end_date: str    # ISO format
    interval: str = '1d'
    initial_capital: float = 100000.0

# In-memory storage for backtest results (TODO: move to database)
backtest_results = {}

@app.post("/api/backtest/run")
async def run_backtest(request: BacktestRequest):
    """Run a backtest with given parameters."""
    try:
        # Parse dates
        start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))
        
        # Create backtest ID
        backtest_id = f"bt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize engine
        engine = BacktestEngine(
            initial_capital=request.initial_capital,
            commission_pct=0.001,
            slippage_pct=0.0005
        )
        
        # Load data
        engine.load_historical_data(
            tickers=request.tickers,
            start_date=start_date,
            end_date=end_date,
            interval=request.interval
        )
        
        # Use Agent Strategy
        from src.backtesting.strategy_adapter import create_agent_strategy
        
        # We can pass a callback here if we want to stream logs via WebSocket in real-time
        # For now, we'll rely on the engine collecting logs and returning them
        strategy_func = create_agent_strategy()
        
        # Run backtest
        results = engine.run(strategy_func, request.tickers)
        
        # Calculate metrics
        metrics = calculate_all_metrics(
            equity_curve=results['equity_curve'],
            trades=results['trades']
        )
        
        # Store results
        backtest_results[backtest_id] = {
            'id': backtest_id,
            'parameters': request.dict(),
            'equity_curve': results['equity_curve'].to_dict(orient='records'),
            'trades': results['trades'],
            'matched_trades': results.get('matched_trades', []),
            'agent_logs': results.get('agent_logs', []),
            'metrics': metrics,
            'created_at': datetime.now().isoformat()
        }
        
        return {
            'backtest_id': backtest_id,
            'status': 'completed',
            'metrics': metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backtest/results/{backtest_id}")
async def get_backtest_results(backtest_id: str):
    """Get results for a specific backtest."""
    if backtest_id not in backtest_results:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    return backtest_results[backtest_id]
