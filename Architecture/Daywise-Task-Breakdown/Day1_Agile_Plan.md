# Cortex5 - Day 1: The Council of Agents & Infrastructure Foundation
## Methodology: Agile Scrum (Epics > Stories > Tasks)
**Goal**: Initialize the project, set up the infrastructure (Docker/K8s), and spawn the 5 AI Agents using LangGraph.

---

## 📊 Progress Tracker
*(Update this section as you complete tasks using the Vibe Coding workflow)*

- [ ] **Epic 1: Genesis - System Initialization**
    - [ ] Story 1.1: Project Scaffolding
    - [ ] Story 1.2: Container Orchestration (Docker)
    - [ ] Story 1.3: Local Infrastructure (Kubernetes/Kind)
- [ ] **Epic 2: The Council - Agent Orchestration**
    - [ ] Story 2.1: LangGraph State Definition
    - [ ] Story 2.2: The Agent Factory
- [ ] **Epic 3: Recruitment - Agent Configuration**
    - [ ] Story 3.1: Data & Sentiment Agents
    - [ ] Story 3.2: Quant, Risk & Execution Agents

---

## 🚀 Epic 1: Genesis - System Initialization
**Objective**: Create the physical and digital environment for the Hedge Fund to exist.

### Story 1.1: Project Scaffolding
**Description**: Set up the Python project structure, virtual environment, and dependency management.

*   **Task 1.1.1**: Initialize Git and Python Project Structure.
    *   **Agent Prompt**:
        > "Act as a Senior DevOps Engineer. Initialize a new Python project named 'ai-hedge-fund'. Create the following directory structure: `src/agents`, `src/data`, `src/utils`, `k8s`, `terraform`, `tests`. Create a `.gitignore` for Python and a `pyproject.toml` managing dependencies for `langgraph`, `fastapi`, `qdrant-client`, `timescaledb-client`, `torch`, and `pydantic`."

*   **Task 1.1.2**: Configure Pre-commit Hooks & Linting.
    *   **Agent Prompt**:
        > "Set up `ruff` for linting and formatting in `pyproject.toml`. Create a `.pre-commit-config.yaml` that runs `ruff check` and `ruff format` on every commit. Ensure strict type checking is enabled."

### Story 1.2: Container Orchestration (Docker)
**Description**: Define the local development environment using Docker Compose.

*   **Task 1.2.1**: Define Hybrid Database Containers.
    *   **Agent Prompt**:
        > "Create a `docker-compose.yml` file. Define two services:
        > 1. `timescaledb`: Use image `timescale/timescaledb:latest-pg16`. Expose port 5432. Add a volume `pgdata:/var/lib/postgresql/data`.
        > 2. `qdrant`: Use image `qdrant/qdrant:v1.16.0`. Expose port 6333. Add a volume `qdrant_storage:/qdrant/storage`.
        > Ensure both services are on a network named `hedge-net`."

*   **Task 1.2.2**: Define Inference Engine Container.
    *   **Agent Prompt**:
        > "Add an `ollama` service to the `docker-compose.yml`. Use image `ollama/ollama:latest`. Expose port 11434. Mount a volume `ollama_models:/root/.ollama` to persist models. Configure it to pull `llama3:8b-instruct-q4_K_M` on startup if possible, or write a startup script `scripts/start_ollama.sh` to do so."

### Story 1.3: Local Infrastructure (Kubernetes/Kind)
**Description**: Prepare a local Kubernetes cluster to simulate production deployment.

*   **Task 1.3.1**: Install & Configure Kind (Kubernetes in Docker).
    *   **Agent Prompt**:
        > "Act as a DevOps Engineer. Create a `k8s/kind-config.yaml` to define a local Kubernetes cluster using `kind`. Configure it with 1 control-plane node and 2 worker nodes. Map port 80 on the host to port 80 on the container (for the Ingress controller)."

*   **Task 1.3.2**: Create Local Registry & Cluster.
    *   **Agent Prompt**:
        > "Write a shell script `scripts/setup_cluster.sh` that:
        > 1. Checks if `kind` and `kubectl` are installed.
        > 2. Creates a local docker registry on port 5001.
        > 3. Creates the kind cluster using `k8s/kind-config.yaml`.
        > 4. Connects the registry to the kind network."

---

## 🧠 Epic 2: The Council - Agent Orchestration
**Objective**: Build the brain that connects the agents using LangGraph.

### Story 2.1: LangGraph State Definition
**Description**: Define the shared memory and communication protocol between agents.

*   **Task 2.1.1**: Define the Global State Schema.
    *   **Agent Prompt**:
        > "Using `langgraph` and `pydantic`, define the `AgentState` class in `src/graph.py`. It must include:
        > - `messages`: A list of LangChain `BaseMessage`.
        > - `market_data`: A dictionary to hold OHLCV data.
        > - `sentiment_score`: A float (0.0 to 1.0).
        > - `trade_signal`: Enum ('BUY', 'SELL', 'HOLD').
        > - `risk_approval`: Boolean.
        > - `execution_status`: String."

### Story 2.2: The Agent Factory
**Description**: Create a reusable base class for all agents to inherit from.

*   **Task 2.2.1**: Implement Base Agent Class.
    *   **Agent Prompt**:
        > "Create `src/agents/base_agent.py`. Define a class `BaseAgent` that takes a `name`, `model` (LLM), and `tools` list. Implement a method `run(state: AgentState) -> dict` that invokes the LLM with the current state and returns the updated state keys. Use structured output parsing to ensure the LLM respects the State schema."

---

## 👥 Epic 3: Recruitment - Agent Configuration
**Objective**: Spawn the specific agents with their unique personalities and system prompts.

### Story 3.1: Data & Sentiment Agents
**Description**: The "Eyes and Ears" of the fund.

*   **Task 3.1.1**: Configure Data Agent.
    *   **Agent Prompt**:
        > "Create `src/agents/data_agent.py`. Inherit from `BaseAgent`.
        > **System Prompt**: 'You are the Data Engineer. Your job is to fetch raw OHLCV data from Yahoo Finance and query TimescaleDB. You do not analyze, you only provide facts.'
        > **Tools**: Implement a tool `fetch_stock_data(ticker: str)` using `yfinance`."

*   **Task 3.1.2**: Configure Sentiment Agent.
    *   **Agent Prompt**:
        > "Create `src/agents/sentiment_agent.py`. Inherit from `BaseAgent`.
        > **System Prompt**: 'You are the Sentiment Analyst. Your job is to read news headlines and output a sentiment score between 0 (Bearish) and 1 (Bullish). You use the Qdrant vector DB to find similar historical news.'
        > **Tools**: Implement a tool `query_news_vectors(query: str)` using `qdrant_client`."

### Story 3.2: Quant, Risk & Execution Agents
**Description**: The "Brain and Hands" of the fund.

*   **Task 3.2.1**: Configure Quant Analyst Agent.
    *   **Agent Prompt**:
        > "Create `src/agents/quant_agent.py`.
        > **System Prompt**: 'You are the Quant Researcher. You analyze the `market_data` provided by the Data Agent and the `sentiment_score` from the Sentiment Agent. You output a `trade_signal` (BUY/SELL/HOLD) based on technical indicators like RSI and MACD.'
        > **Logic**: Implement a Python function `calculate_rsi` to assist the LLM."

*   **Task 3.2.2**: Configure Risk Manager Agent.
    *   **Agent Prompt**:
        > "Create `src/agents/risk_agent.py`.
        > **System Prompt**: 'You are the Risk Manager. You are the gatekeeper. You review the `trade_signal`. If the signal is BUY, check if we have enough capital. If the volatility is too high, set `risk_approval` to False. You are conservative and paranoid.'
        > **Rule**: Reject any trade if `sentiment_score` < 0.5 for a BUY signal."

*   **Task 3.2.3**: Configure Execution Trader Agent.
    *   **Agent Prompt**:
        > "Create `src/agents/execution_agent.py`.
        > **System Prompt**: 'You are the Head Trader. You only execute if `risk_approval` is True. You log the trade details into the `execution_status` field.'
        > **Tools**: Create a mock tool `execute_order(symbol, side, quantity)` that prints to console."

---

## 🔗 Orchestration Wiring (End of Day 1)

*   **Task 4.0**: Wire the Graph.
    *   **Agent Prompt**:
        > "In `src/graph.py`, use `StateGraph` from `langgraph`. Add nodes for all 5 agents.
        > **Edges**:
        > `START` -> `DataAgent` -> `SentimentAgent` -> `QuantAgent` -> `RiskAgent` -> `ExecutionAgent` -> `END`.
        > Compile the graph and expose it as `app`."

---

## 📝 Definition of Done (Day 1)
1.  `docker-compose up` starts TimescaleDB, Qdrant, and Ollama without errors.
2.  `scripts/setup_cluster.sh` runs successfully and `kubectl get nodes` shows 3 nodes.
3.  All 5 Agent classes exist in `src/agents/`.
4.  `src/graph.py` compiles without errors.
5.  You can run a dummy script `python main.py` that passes a message through the graph and gets a result from the Execution Agent.
