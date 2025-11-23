# Project: Cortex5 - The Atomic Plan
## First Principles Implementation Guide

**Mission**: Build a scalable, autonomous Hedge Fund with 5 AI Agents using "Vibe Coding" and Antigravity IDE.
**Philosophy**: Break down the system to its atomic units (containers, scripts, schemas) and build upwards.
**Target Environment**: AWS (EKS/EC2) or any Cloud Provider.

---

## 1. The Atomic Elements (Tech Stack & Versions)

We use the latest stable versions as of Nov 2025 to ensure longevity and performance.

### **Infrastructure Atoms**
*   **Language**: Python **3.14.0** (Performance improvements).
*   **Containerization**: Docker Engine **v29.0.0**.
*   **Orchestration**: Kubernetes **1.34.2**.
*   **Cloud CLI**: AWS CLI **2.32.3**.

### **Data Atoms**
*   **Vector Database**: Qdrant **1.16.0** (Rust-based, high performance).
*   **Time-Series Database**: TimescaleDB **2.23.1** (PostgreSQL 18 compatible).
*   **Object Storage**: AWS S3 (Standard).

### **Intelligence Atoms**
*   **Agent Framework**: LangGraph **v1.0.2** (Stateful, graph-based orchestration).
*   **LLM Inference**: Ollama (Latest) running **Llama-3-8B-Instruct**.
*   **ML Framework**: PyTorch **2.9.1**.
*   **Embeddings**: `BAAI/bge-m3` (State-of-the-art multilingual embeddings).

### **Application Atoms**
*   **Backend**: FastAPI **0.121.3**.
*   **Frontend**: Next.js **16** (React framework).
*   **Styling**: Tailwind CSS **4.1.17**.

---

## 2. The Molecular Structure (System Components)

We build molecules from atoms. These are the deployable units.

### **Molecule A: The Data Lakehouse**
*   **Container 1**: `timescaledb` (Port 5432) - Stores OHLCV, Trades, Logs.
*   **Container 2**: `qdrant` (Port 6333) - Stores News Embeddings, Sentiment Vectors.
*   **Volume**: `s3_bucket` - Raw JSON dumps, Model Weights (`.pt` files).

### **Molecule B: The Brain (Inference Engine)**
*   **Container 3**: `ollama-server` (Port 11434) - Exposes LLM API.
*   **Model**: `llama3:8b-instruct-q4_K_M` (Quantized for speed/memory balance).

### **Molecule C: The Council (Agent Runtime)**
*   **Container 4**: `agent-orchestrator` (Python 3.14)
    *   **Data Agent**: `src/agents/data_agent.py`
    *   **Sentiment Agent**: `src/agents/sentiment_agent.py`
    *   **Quant Agent**: `src/agents/quant_agent.py`
    *   **Risk Agent**: `src/agents/risk_agent.py`
    *   **Execution Agent**: `src/agents/execution_agent.py`
    *   **Graph**: `src/graph.py` (LangGraph definition).

### **Molecule D: The Interface**
*   **Container 5**: `backend-api` (FastAPI, Port 8000) - WebSocket bridge.
*   **Container 6**: `frontend-ui` (Next.js 16, Port 3000) - Dashboard.

---

## 3. Step-by-Step Construction (The Build Process)

### **Phase 1: The Foundation (Infrastructure)**
1.  **Setup Environment**:
    ```bash
    # Install Python 3.14
    pyenv install 3.14.0
    pyenv global 3.14.0
    
    # Create Virtual Env
    python -m venv venv
    source venv/bin/activate
    
    # Install Dependencies
    pip install langgraph==1.0.2 torch==2.9.1 fastapi==0.121.3 qdrant-client timescaledb-client
    ```
2.  **Docker Compose (Local Dev)**:
    *   Create `docker-compose.yml` defining `timescaledb`, `qdrant`, and `ollama`.
    *   Ensure networks are bridged so Agents can talk to DBs.

### **Phase 2: The Memory (Data Layer)**
1.  **Schema Definition**:
    *   **SQL**: Create tables for `market_data` (symbol, time, open, high, low, close, volume) and `trade_logs`.
    *   **Vector**: Create Qdrant collection `financial_news` with vector size 1024 (bge-m3).
2.  **Ingestion Scripts**:
    *   Write `ingest_market.py`: Fetch from Yahoo Finance -> Insert to Timescale.
    *   Write `ingest_news.py`: Fetch RSS -> Embed -> Insert to Qdrant.

### **Phase 3: The Intelligence (Agents)**
1.  **Base Agent Class**:
    *   Define `AgentState` in LangGraph (messages, data_context, decision).
2.  **Specific Agent Logic**:
    *   **Data Agent**: Tools to query TimescaleDB.
    *   **Sentiment Agent**: Tools to query Qdrant and summarize with Ollama.
    *   **Quant Agent**: Python function to calculate RSI/MACD and decide BUY/SELL.
    *   **Risk Agent**: Python function to check portfolio limits.
    *   **Execution Agent**: Mock API call to broker.
3.  **Graph Construction**:
    *   Define Nodes (Agents) and Edges (Flow).
    *   `Data -> Sentiment -> Quant -> Risk -> Execution`.

### **Phase 4: The Nervous System (API & UI)**
1.  **FastAPI Backend**:
    *   Endpoint `/stream`: WebSocket for real-time agent logs.
    *   Endpoint `/portfolio`: GET current value.
2.  **Next.js Frontend**:
    *   `npx create-next-app@16`
    *   Use Tailwind v4 for styling.
    *   Components: `AgentStatus`, `PriceChart`, `TradeLog`.

### **Phase 5: Deployment (Cloud)**
1.  **Dockerize**:
    *   Write `Dockerfile` for Python services (Multi-stage build to keep it light).
    *   Write `Dockerfile` for Next.js (Standalone output).
2.  **Kubernetes Manifests**:
    *   `deployment.yaml`: Define pods for Agents, API, UI.
    *   `service.yaml`: Expose UI (LoadBalancer) and API (ClusterIP).
    *   `pvc.yaml`: Persistent Volume for DBs.
3.  **Deploy**:
    *   `kubectl apply -f k8s/`

---

## 4. Verification & Testing (Quality Assurance)
*   **Unit Tests**: `pytest` for individual agent logic (e.g., does Risk Agent reject >2% allocation?).
*   **Integration Tests**: Run the full LangGraph with mock data.
*   **Vibe Check**: Manually verify the UI updates when a "trade" happens in the logs.

---

## 5. Future Proofing
*   **MLOps**: Add MLflow for tracking model finetuning experiments.
*   **Scaling**: Move from local Ollama to AWS Bedrock or Sagemaker endpoints if load increases.
*   **Security**: Implement API Keys and JWT Auth for the Dashboard.

This plan serves as the **Master Blueprint**. Refer to this for every code change.
