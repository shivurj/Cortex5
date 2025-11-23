# Project: Cortex5 - Vibe Coding Implementation Plan
## Powered by Google Antigravity IDE

**Goal**: Build a Single Person + 5 AI Agents Hedge Fund in 7 Days using "Vibe Coding".

---

## What is Vibe Coding in Antigravity?
**Vibe Coding** is a development paradigm where you focus on the **intent** (the "vibe" or high-level goal) and let the AI Agents in Antigravity handle the **implementation**. Instead of writing every line of Python, you act as the **Chief Architect**, orchestrating agents to build components.

**Antigravity IDE Features to Use:**
*   **Agent Manager**: Spawn and manage the 5 specialized agents (Data, Sentiment, Quant, Risk, Execution).
*   **Editor Vibe View**: Highlight code/folders and type natural language instructions (e.g., "Refactor this to use Qdrant for vector storage").
*   **Manager View**: Watch agents work in parallel on different files.

---

## 7-Day Implementation Roadmap

### Day 1: The Council of Agents (Setup & Orchestration)
**Goal**: Initialize the project and spawn your 5 AI employees.

1.  **Project Initialization**:
    *   Open Antigravity.
    *   Prompt: *"Create a new Python project structure for a hedge fund with 5 distinct agent modules: Data, Sentiment, Quant, Risk, Execution. Use LangGraph for orchestration."*
2.  **Agent Configuration**:
    *   Open **Agent Manager**.
    *   Create 5 Agents with specific system prompts (copy from Architecture doc).
    *   *Vibe Check*: *"Verify that the Data Agent can talk to the Quant Agent via the LangGraph state."*
3.  **Infrastructure as Code**:
    *   Prompt: *"Generate Terraform files to set up an AWS EKS cluster and an S3 bucket for our data lake."*

### Day 2: The Data Foundation (Ingestion & Storage)
**Goal**: Get data flowing into the system.

1.  **Hybrid DB Setup**:
    *   Prompt: *"Create a docker-compose file running PostgreSQL (with TimescaleDB) and Qdrant. Expose ports 5432 and 6333."*
2.  **Data Ingestion Pipelines**:
    *   **Data Agent Task**: *"Write a script to fetch historical OHLCV data from Yahoo Finance and store it in TimescaleDB. Handle rate limits."*
    *   **Sentiment Agent Task**: *"Create a pipeline to scrape financial news from RSS feeds and ingest embeddings into Qdrant using `BAAI/bge-m3` model."*
3.  **Vibe Coding**: Highlight the ingestion script -> *"Make this async and add error handling for network drops."*

### Day 3: The Brain (Model Training & Finetuning)
**Goal**: Teach the AI how to understand markets.

1.  **Local Inference Setup**:
    *   Prompt: *"Set up a local Ollama instance running Llama-3-8B-Instruct. Create a Python wrapper class to interface with it."*
2.  **Finetuning Pipeline**:
    *   **Quant Agent Task**: *"Create a PyTorch training loop to finetune a Llama-3 model on our historical financial news data using LoRA (PEFT). Save adapters to S3."*
3.  **Validation**:
    *   Prompt: *"Run a test inference: Ask the finetuned model to summarize a sample earnings call."*

### Day 4: The Strategy (Signal Generation)
**Goal**: Define the logic for buying and selling.

1.  **Strategy Logic**:
    *   **Quant Agent Task**: *"Implement a strategy that buys if Sentiment Score > 0.8 and RSI < 30. Use the data from TimescaleDB."*
2.  **Backtesting Engine**:
    *   Prompt: *"Build a backtesting engine using `backtrader` or custom Python. It should replay historical data and simulate trades based on the Quant Agent's signals."*
3.  **Optimization**:
    *   *Vibe Coding*: *"Run the backtest on AAPL data from 2023. Optimize the RSI parameters to maximize Sharpe Ratio."*

### Day 5: The Guardrails (Risk & Execution)
**Goal**: Ensure we don't lose all the money and can actually trade.

1.  **Risk Management**:
    *   **Risk Agent Task**: *"Implement a pre-trade check. Reject any order that exceeds 2% of portfolio value or if daily drawdown > 5%."*
2.  **Execution Bridge**:
    *   **Execution Agent Task**: *"Create a mock broker API class. Then implement the order execution logic that receives signals, checks with Risk Agent, and places orders."*
3.  **Integration Test**:
    *   Prompt: *"Simulate a full trade lifecycle: Data -> Signal -> Risk Check -> Execution. Log every step."*

### Day 6: The Face (Dashboard & UI)
**Goal**: See what's happening in real-time.

1.  **Frontend Generation**:
    *   Prompt: *"Generate a Next.js dashboard with a dark, futuristic financial aesthetic. Use TailwindCSS."*
    *   *Vibe Coding*: *"Add a real-time chart widget using Recharts that connects to our WebSocket API."*
2.  **API Layer**:
    *   Prompt: *"Create FastAPI endpoints to serve portfolio value, active trades, and agent status logs."*

### Day 7: Launch & Observe (Deployment)
**Goal**: Go live (or simulated live).

1.  **Containerization**:
    *   Prompt: *"Create Dockerfiles for the API, the Agent Orchestrator, and the Frontend."*
2.  **Deployment**:
    *   Prompt: *"Deploy the stack to the local Kubernetes cluster defined in Day 1."*
3.  **Final Vibe Check**:
    *   Sit back and watch the **Manager View** in Antigravity. Monitor the agents as they process live data and generate signals.
    *   Iterate by highlighting "lazy" agents and prompting: *"You are missing signals, increase your sensitivity to news events."*

---

## Summary of Logical Steps
1.  **Define Agents**: Who does what? (Day 1)
2.  **Build Data Lake**: Where does knowledge live? (Day 2)
3.  **Train Brains**: How do they learn? (Day 3)
4.  **Codify Strategy**: When to act? (Day 4)
5.  **Enforce Safety**: How to stay safe? (Day 5)
6.  **Visualize**: What is happening? (Day 6)
7.  **Deploy**: Let it run. (Day 7)

**Pro Tip**: In Antigravity, if an agent gets stuck, don't fix the code yourself. **Fix the prompt**. Treat the agents like junior developers who need clear instructions.
