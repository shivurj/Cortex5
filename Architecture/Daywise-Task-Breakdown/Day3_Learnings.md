# Cortex 5 - Day 3 Technical Learning Guide: The Nervous System (API & UI)

## 📝 Executive Summary
Day 3 transformed Cortex5 from a backend-only system into a **full-stack AI hedge fund** with real-time visualization. We implemented:
- **FastAPI backend** with REST endpoints and WebSocket streaming
- **Next.js dashboard** with real-time agent visualization
- **Event-driven architecture** connecting agents to the UI
- **Modern "tech-noir" interface** for monitoring the AI council

---

## 1. Architecture Deep Dive

### 1.1 The Communication Layer: FastAPI Backend
This layer exposes the agent system to the outside world.

```ascii
[Frontend (Next.js)]
        |
        | HTTP/WS
        v
[FastAPI Server :8000]
        |
        +---> [REST Endpoints]
        |       |
        |       +---> GET /health
        |       +---> GET /api/trades
        |       +---> GET /api/portfolio
        |       +---> GET /api/market-data/{ticker}
        |
        +---> [WebSocket /ws/stream]
                |
                v
        [ConnectionManager]
                |
                v (broadcast)
        [All Connected Clients]
```

**Technical Details:**
- **CORS Middleware**: Configured to allow `http://localhost:3000` (Next.js dev server)
- **Connection Pooling**: Database client initialized on startup, shared across requests
- **Async/Await**: All endpoints are async for non-blocking I/O
- **WebSocket Protocol**: Uses JSON messages with `type`, `agent`, `message`, `timestamp` fields

### 1.2 The Real-Time Pipeline: WebSocket Event Streaming
This is the "nervous system" that transmits agent thoughts to the UI.

```ascii
[Agent Graph Execution]
        |
        v (callback)
[BaseAgent.log()]
        |
        v (sync_callback wrapper)
[asyncio.run_coroutine_threadsafe]
        |
        v (event loop)
[ConnectionManager.broadcast()]
        |
        v (WebSocket)
[Frontend useAgentStream Hook]
        |
        v (state update)
[React Components Re-render]
```

**Technical Details:**
- **Thread Safety**: Agents run in a separate thread (`asyncio.to_thread`), callbacks use `run_coroutine_threadsafe` to safely communicate with the async event loop
- **Event Types**: `status`, `info`, `success`, `error`, `result`
- **Payload Structure**:
  ```json
  {
    "agent": "DataAgent",
    "message": "Fetching data from Yahoo Finance...",
    "type": "status",
    "data": {"ticker": "AAPL"},
    "timestamp": "2025-11-23T18:46:09+05:30"
  }
  ```

### 1.3 The Visual Interface: Next.js Dashboard
Modern React-based UI with real-time updates.

```ascii
[Dashboard Page]
        |
        +---> [useAgentStream Hook]
        |       |
        |       +---> WebSocket Connection
        |       +---> State Management (logs, activeAgent, tradeDecision)
        |
        +---> [AgentStatus Component]
        |       |
        |       +---> Visual Pipeline (5 agents)
        |       +---> Active Agent Highlighting
        |
        +---> [PriceChart Component]
        |       |
        |       +---> Recharts Line Chart
        |       +---> Fetches from /api/market-data
        |
        +---> [TradeLog Component]
                |
                +---> Table of Executions
                +---> Polls /api/trades every 5s
```

---

## 2. Component Analysis (Deep Technical)

### 2.1 FastAPI WebSocket Manager
**Why a Manager Class?**
WebSockets are stateful connections. We need to track all active clients to broadcast messages.

**Implementation Pattern:**
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)
```

**Key Insight**: We use a **singleton pattern** (`manager = ConnectionManager()`) so all parts of the API share the same connection list.

### 2.2 Agent Callback Mechanism
**The Challenge**: Agents run synchronously, but WebSocket broadcast is async.

**The Solution**: A three-layer bridge:
1. **BaseAgent.log()**: Synchronous method that agents call
2. **sync_callback()**: Wrapper that uses `asyncio.run_coroutine_threadsafe()`
3. **manager.broadcast()**: Async method that sends to WebSocket

**Code Flow:**
```python
# In src/api/main.py
def sync_callback(payload):
    asyncio.run_coroutine_threadsafe(manager.broadcast(payload), loop)

# In src/agents/base_agent.py
def log(self, message: str, type: str = "info", data: Any = None):
    if asyncio.iscoroutinefunction(self.callback):
        loop = asyncio.get_running_loop()
        loop.create_task(self.callback(payload))
```

**Why This Works**: `run_coroutine_threadsafe` schedules the coroutine in the main event loop from a worker thread, ensuring thread safety.

### 2.3 React Custom Hook: useAgentStream
**Purpose**: Encapsulate WebSocket logic and provide clean state to components.

**State Management:**
- `isConnected`: Boolean for connection status
- `activeAgent`: Currently executing agent (DataAgent, SentimentAgent, etc.)
- `logs`: Array of all messages received
- `tradeDecision`: Final result from ExecutionAgent

**Message Handling:**
```typescript
const handleMessage = (data: any) => {
    const { type, agent, message, timestamp, data: payload } = data;
    
    if (type === 'status' && agent !== 'System') {
        setActiveAgent(agent);  // Highlight the active agent
    }
    
    if (type === 'result' && agent === 'ExecutionAgent') {
        setActiveAgent(null);  // Clear highlight
        setTradeDecision(payload);  // Store final decision
    }
    
    setLogs((prev) => [...prev, {...}]);  // Append to log
};
```

### 2.4 Tailwind CSS "Tech-Noir" Design System
**Color Palette:**
- Background: `slate-950` (near black)
- Panels: `slate-900` (dark gray)
- Borders: `slate-800` (medium gray)
- Text: `slate-200` (light gray)
- Accent: `emerald-500` (bright green)

**Key Patterns:**
- **Glassmorphism**: `bg-slate-900/50 backdrop-blur-md`
- **Glow Effects**: `ring-2 ring-emerald-500 animate-pulse`
- **Monospace Fonts**: `font-mono` for technical data (tickers, timestamps)

---

## 3. Challenges & Solutions (The "Gotchas")

### 🐛 Bug 1: Async/Sync Mismatch in Callbacks
**The Issue**: Agents are synchronous (LangGraph nodes), but WebSocket broadcast is async. Calling `await` in a sync function causes `SyntaxError`.

**The Fix**: Use `asyncio.run_coroutine_threadsafe()` to bridge the gap.
```python
def sync_callback(payload):
    asyncio.run_coroutine_threadsafe(manager.broadcast(payload), loop)
```

**Why**: This schedules the async function in the event loop without blocking the sync code.

### 🐛 Bug 2: WebSocket Connection Timing
**The Issue**: If the frontend connects before the backend starts, the connection fails silently.

**The Fix**: Add connection status indicator in the UI and retry logic.
```typescript
ws.onclose = () => {
    setIsConnected(false);
    addLog('System', 'Disconnected from Cortex5 Neural Link', 'error');
};
```

**Production Note**: Implement exponential backoff reconnection logic.

### 🐛 Bug 3: Next.js "use client" Directive
**The Issue**: React hooks (useState, useEffect) only work in Client Components, but Next.js 13+ defaults to Server Components.

**The Fix**: Add `"use client"` at the top of files using hooks.
```typescript
"use client";

import { useState } from 'react';
```

**Why**: This tells Next.js to render this component on the client side where browser APIs (WebSocket) are available.

---

## 4. Key Code Patterns

### 4.1 FastAPI Dependency Injection
Using `@app.on_event` for lifecycle management.
```python
@app.on_event("startup")
def startup_db():
    db.connect()

@app.on_event("shutdown")
def shutdown_db():
    db.close()
```

### 4.2 React State Updates with Functional Updates
Avoiding stale closures in WebSocket callbacks.
```typescript
// BAD: Captures old state
setLogs(logs.concat(newLog));

// GOOD: Uses latest state
setLogs((prev) => [...prev, newLog]);
```

### 4.3 TypeScript Interface for Type Safety
Defining message structure for WebSocket payloads.
```typescript
export interface AgentLog {
  timestamp: string;
  agent: AgentType;
  message: string;
  type: 'info' | 'error' | 'success' | 'status' | 'result';
  data?: any;
}
```

---

## 5. Performance Considerations

### 5.1 WebSocket vs Polling
**Why WebSocket?**
- **Latency**: ~10ms vs 1000ms+ for polling
- **Efficiency**: Single persistent connection vs repeated HTTP requests
- **Real-time**: Instant updates as agents think

### 5.2 React Rendering Optimization
**Potential Issue**: Every log message triggers a re-render of the entire dashboard.

**Future Optimization**: Use `React.memo()` on components that don't depend on logs.
```typescript
export const AgentStatus = React.memo(({ activeAgent }) => {
    // Only re-renders when activeAgent changes
});
```

### 5.3 Database Query Optimization
**Current**: TradeLog polls every 5 seconds.
**Better**: Push updates via WebSocket when trades execute.
```python
# In ExecutionAgent
self.log(status, "success")
# Triggers broadcast to frontend, no polling needed
```

---

## 6. Architecture Decisions

### 6.1 Why FastAPI over Flask?
- **Async Native**: Built on ASGI (Starlette), perfect for WebSockets
- **Type Hints**: Automatic validation with Pydantic
- **Performance**: 2-3x faster than Flask for I/O-bound tasks
- **Auto Docs**: Built-in Swagger UI at `/docs`

### 6.2 Why Next.js over Create React App?
- **Server-Side Rendering**: Better SEO and initial load time
- **File-based Routing**: `app/page.tsx` → `/`
- **Built-in Optimization**: Image optimization, code splitting
- **TypeScript First**: Better DX with type safety

### 6.3 Why Recharts over Chart.js?
- **React Native**: Declarative API, no imperative DOM manipulation
- **Composability**: `<LineChart><Line /><XAxis /></LineChart>`
- **Responsive**: Built-in responsive container

---

## 7. Future Enhancements (Production Readiness)

1. **Authentication**: Add JWT tokens for WebSocket connections
2. **Rate Limiting**: Prevent WebSocket message flooding
3. **Error Boundaries**: React error boundaries to catch component crashes
4. **Logging**: Structured logging with correlation IDs (trace requests across services)
5. **Monitoring**: Add Prometheus metrics for WebSocket connections, message throughput
6. **Horizontal Scaling**: Use Redis Pub/Sub for multi-instance WebSocket broadcasting

---

## 8. Testing Strategy

### 8.1 Backend Tests
```python
# Test WebSocket connection
async def test_websocket_stream():
    async with AsyncClient(app=app, base_url="http://test") as client:
        async with client.websocket_connect("/ws/stream") as ws:
            await ws.send_json({"action": "analyze", "ticker": "AAPL"})
            data = await ws.receive_json()
            assert data["type"] == "status"
```

### 8.2 Frontend Tests
```typescript
// Test useAgentStream hook
import { renderHook, act } from '@testing-library/react-hooks';

test('connects to WebSocket', () => {
    const { result } = renderHook(() => useAgentStream());
    expect(result.current.isConnected).toBe(true);
});
```

---

**Day 3 Status**: ✅ **IMPLEMENTATION COMPLETE**
**Next Milestone**: Day 4 - Backtesting Engine & Performance Analytics

---

## 9. Quick Reference Commands

### Start Backend
```bash
cd /Volumes/Dhitva/Bots/Interview_Prep/Cortex5
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
cd /Volumes/Dhitva/Bots/Interview_Prep/Cortex5/frontend
npm run dev
```

### Access Points
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:3000
- **Health Check**: http://localhost:8000/health
