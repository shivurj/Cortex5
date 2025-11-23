# Cortex5 AI Hedge Fund

An autonomous AI-powered hedge fund system built with LangGraph, Docker, and Kubernetes. Cortex5 employs a "Council of Agents" architecture where specialized AI agents collaborate to analyze market data, assess sentiment, and execute trades.

## 🏗 Architecture

The system consists of 5 specialized agents orchestrated by a State Graph:

1.  **Data Agent**: Fetches raw OHLCV data from Yahoo Finance.
2.  **Sentiment Agent**: Analyzes news sentiment (simulated with Qdrant vector search).
3.  **Quant Agent**: Performs technical analysis (RSI, MACD) on market data.
4.  **Risk Agent**: Validates trade signals against risk parameters and capital availability.
5.  **Execution Agent**: Executes approved trades and logs them.

### Tech Stack
-   **Orchestration**: LangGraph, LangChain
-   **LLM**: Ollama (Llama 3.2, Gemma, etc.)
-   **Database**: TimescaleDB (Time-series), Qdrant (Vector DB)
-   **Infrastructure**: Docker Compose, Kubernetes (Kind)
-   **Language**: Python 3.10+

## 🚀 Getting Started

### Prerequisites
-   [Docker Desktop](https://www.docker.com/products/docker-desktop/)
-   [Kind](https://kind.sigs.k8s.io/) (`brew install kind`)
-   [Kubectl](https://kubernetes.io/docs/tasks/tools/) (`brew install kubectl`)
-   [Python 3.10+](https://www.python.org/)
-   [Ollama](https://ollama.com/) (for local LLM inference)

### 1. Clone the Repository
```bash
git clone https://github.com/shivurj/Cortex5.git
cd Cortex5
```

### 2. Configure Environment
Copy the example environment file and configure your LLM settings. By default, the project uses Ollama with `llama3.2:3b`.

```bash
cp .env.example .env
```

**Note**: Ensure you have the model pulled in Ollama:
```bash
ollama pull llama3.2:3b
```

### 3. Start Infrastructure
Start the database services (TimescaleDB, Qdrant) using Docker Compose:

```bash
docker-compose up -d timescaledb qdrant
```

### 4. Install Dependencies
Create a virtual environment and install the project dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 5. Run the Agents
Execute the main script to see the agents in action:

```bash
python main.py
```

## ☸️ Kubernetes Setup (Local)
To simulate a production deployment using Kind:

1.  **Setup Cluster**:
    ```bash
    ./scripts/setup_cluster.sh
    ```
    This script creates a local Kind cluster with a Docker registry.

2.  **Verify Nodes**:
    ```bash
    kubectl get nodes
    ```

## 📂 Project Structure
```
Cortex5/
├── Architecture/       # Design docs and plans
├── k8s/               # Kubernetes manifests
├── scripts/           # Helper scripts
├── src/
│   ├── agents/        # Agent implementations
│   ├── data/          # Data handling logic
│   ├── utils/         # Utility functions
│   ├── graph.py       # LangGraph definition
│   └── state.py       # Global state schema
├── docker-compose.yml # Local infrastructure
├── main.py            # Entry point
└── pyproject.toml     # Dependencies
```

## 🤝 Contributing
1.  Fork the repository
2.  Create your feature branch (`git checkout -b feature/amazing-feature`)
3.  Commit your changes (`git commit -m 'Add some amazing feature'`)
4.  Push to the branch (`git push origin feature/amazing-feature`)
5.  Open a Pull Request
