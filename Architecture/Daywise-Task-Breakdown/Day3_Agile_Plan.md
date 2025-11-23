# Cortex5 - Day 3: The Nervous System (API & UI)
## Methodology: Agile Scrum (Epics > Stories > Tasks)
**Goal**: Build the "Nervous System" of the hedge fund - a FastAPI backend to expose agent internals and a Next.js dashboard to visualize the "Council of Agents" in real-time.

---

## 📊 Progress Tracker
*(Update this section as you complete tasks using the Vibe Coding workflow)*

- [ ] **Epic 1: The Synapse - API Layer**
    - [ ] Story 1.1: FastAPI Setup & Endpoints
    - [ ] Story 1.2: WebSocket Event Streaming
- [ ] **Epic 2: The Retina - Frontend Dashboard**
    - [ ] Story 2.1: Next.js Setup & UI Shell
    - [ ] Story 2.2: Real-time Agent Visualization
    - [ ] Story 2.3: Market Data & Trade Visualization
- [ ] **Epic 3: The Connection - Integration**
    - [ ] Story 3.1: Connecting Brain to Nervous System
    - [ ] Story 3.2: End-to-End Verification

---

## 🔌 Epic 1: The Synapse - API Layer
**Objective**: Create a high-performance API to serve data and stream real-time agent events to the UI.

### Story 1.1: FastAPI Setup & Endpoints
**Description**: Initialize the FastAPI application and create REST endpoints for static data.

*   **Task 1.1.1**: Initialize FastAPI App.
    *   **Agent Prompt**:
        > "Create `src/api/main.py`. Initialize a `FastAPI` app with CORS middleware allowing `http://localhost:3000`.
        > Add a health check endpoint `GET /health` returning `{'status': 'ok', 'timestamp': ...}`.
        > Use `uvicorn` to run the app on port 8000."

*   **Task 1.1.2**: Create Portfolio & Trade Endpoints.
    *   **Agent Prompt**:
        > "Update `src/api/main.py`. Add endpoints:
        > - `GET /api/trades`: Query `trade_logs` from TimescaleDB (limit 50, desc).
        > - `GET /api/portfolio`: Return current cash and positions (mocked for now or read from a `portfolio` table if we add one).
        > Use `src/data/db_client.py` to fetch data."

### Story 1.2: WebSocket Event Streaming
**Description**: Implement a WebSocket endpoint to stream agent thoughts and actions in real-time.

*   **Task 1.2.1**: Create WebSocket Manager.
    *   **Agent Prompt**:
        > "Create `src/api/websocket_manager.py`. Implement `ConnectionManager` class to handle active websocket connections.
        > Methods: `connect`, `disconnect`, `broadcast(message: dict)`.
        > This will be used to push updates to the frontend."

*   **Task 1.2.2**: Implement Stream Endpoint.
    *   **Agent Prompt**:
        > "Update `src/api/main.py`. Add `WebSocket /ws/stream`.
        > On connection, add client to `ConnectionManager`.
        > Keep connection open and handle disconnects.
        > Create a function `trigger_analysis(ticker: str)` that runs the Agent Graph in a background thread and pushes events to the WebSocket."

---

## 🖥️ Epic 2: The Retina - Frontend Dashboard
**Objective**: Build a modern, "Cyberpunk" style dashboard to monitor the AI hedge fund.

### Story 2.1: Next.js Setup & UI Shell
**Description**: Initialize the frontend project with Tailwind CSS.

*   **Task 2.1.1**: Initialize Next.js App.
    *   **Agent Prompt**:
        > "Initialize a Next.js 14+ app in `frontend/`. Use TypeScript, Tailwind CSS, and ESLint.
        > Clean up the default boilerplate.
        > Install `lucide-react` for icons and `recharts` for charts."

*   **Task 2.1.2**: Create App Layout.
    *   **Agent Prompt**:
        > "Create a dark-mode layout in `frontend/src/app/layout.tsx`.
        > Use a sidebar navigation (Dashboard, Trades, Settings).
        > Apply a 'tech-noir' color palette (slate-900 background, emerald-500 accents)."

### Story 2.2: Real-time Agent Visualization
**Description**: Create components to show which agent is thinking and what they are doing.

*   **Task 2.2.1**: Create Agent Status Component.
    *   **Agent Prompt**:
        > "Create `frontend/src/components/AgentStatus.tsx`.
        > Visual representation of the 5 agents (Data, Sentiment, Quant, Risk, Execution).
        > Highlight the active agent based on props.
        > Show the latest log message/thought bubble for the active agent."

*   **Task 2.2.2**: Implement WebSocket Hook.
    *   **Agent Prompt**:
        > "Create `frontend/src/hooks/useAgentStream.ts`.
        > Connect to `ws://localhost:8000/ws/stream`.
        > Listen for messages and update a local state object containing: `activeAgent`, `logs`, `tradeDecision`."

### Story 2.3: Market Data & Trade Visualization
**Description**: Display the financial data and results.

*   **Task 2.3.1**: Create Price Chart Component.
    *   **Agent Prompt**:
        > "Create `frontend/src/components/PriceChart.tsx` using Recharts.
        > Fetch OHLCV data from `GET /api/market-data/{ticker}` (need to add this endpoint to API too).
        > Display a simple line or candlestick chart."

*   **Task 2.3.2**: Create Trade Log Table.
    *   **Agent Prompt**:
        > "Create `frontend/src/components/TradeLog.tsx`.
        > Fetch trades from `GET /api/trades`.
        > Render a table with columns: Time, Symbol, Side, Price, Status.
        > Style 'BUY' in green and 'SELL' in red."

---

## 🔗 Epic 3: The Connection - Integration
**Objective**: Wire everything together so the user can trigger an analysis from the UI.

### Story 3.1: Connecting Brain to Nervous System
**Description**: Modify the Agent Graph to emit events to the WebSocket.

*   **Task 3.1.1**: Add Callbacks to Agents.
    *   **Agent Prompt**:
        > "Update `src/graph.py` or `src/agents/base_agent.py`.
        > Add a mechanism to accept a `callback` function.
        > In each agent's `run` method, call the callback with `{'agent': 'Name', 'status': 'Thinking...', 'data': ...}`.
        > In `src/api/main.py`, pass the `websocket_manager.broadcast` as the callback when running the graph."

### Story 3.2: End-to-End Verification
**Description**: Verify the full loop.

*   **Task 3.2.1**: Manual Test.
    *   **Agent Prompt**:
        > "Run backend and frontend.
        > In UI, enter 'AAPL' and click 'Analyze'.
        > Verify:
        > 1. Agent icons light up in sequence.
        > 2. Logs appear in real-time.
        > 3. Final trade decision is shown.
        > 4. Trade appears in the Trade Log table."

---

## 📝 Definition of Done (Day 3)
1.  FastAPI server running on port 8000.
2.  Next.js dashboard running on port 3000.
3.  WebSocket connection established and stable.
4.  User can trigger analysis for a ticker from the UI.
5.  UI updates in real-time as agents work.
6.  Trades are persisted to DB and visible in the UI table.
7.  Code is committed to git.
