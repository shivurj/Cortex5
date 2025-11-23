# Cortex5 AI Hedge Fund

An autonomous AI-powered hedge fund system built with LangGraph, Docker, and Kubernetes. Cortex5 employs a "Council of Agents" architecture where specialized AI agents collaborate to analyze market data, assess sentiment, and execute trades.

## 🏗 Architecture

The system consists of 5 specialized agents orchestrated by a State Graph:

1.  **Data Agent**: Fetches OHLCV data from Yahoo Finance, validates it, and stores in TimescaleDB.
2.  **Sentiment Agent**: Performs RAG-based sentiment analysis using Qdrant vector search and LLM.
3.  **Quant Agent**: Performs technical analysis (RSI, MACD) with crossover detection.
4.  **Risk Agent**: Multi-factor validation (position size, volatility, sentiment, capital).
5.  **Execution Agent**: Logs approved trades to TimescaleDB.

### Tech Stack
-   **Orchestration**: LangGraph, LangChain
-   **LLM**: Ollama (Llama 3.2:3b)
-   **Databases**: 
    -   TimescaleDB (Time-series OHLCV data)
    -   Qdrant (Vector DB for news embeddings)
-   **Data Sources**: Yahoo Finance (market data), Google Finance RSS / NewsAPI (news)
-   **ML**: Sentence Transformers (BAAI/bge-small-en-v1.5)
-   **Infrastructure**: Docker Compose, Kubernetes (Kind)
-   **Language**: Python 3.10+

## ✨ Features

### Day 1: Foundation
- ✅ 5 AI agents with LangGraph orchestration
- ✅ Docker Compose infrastructure
- ✅ Kubernetes (Kind) local deployment
- ✅ Basic agent workflow

### Day 2: Intelligence & Data
- ✅ **Real Market Data**: Yahoo Finance integration with retry logic
- ✅ **Data Validation**: 7-layer OHLCV integrity checks
- ✅ **TimescaleDB**: Hypertables, continuous aggregates, connection pooling
- ✅ **News Ingestion**: Google Finance RSS + NewsAPI with caching
- ✅ **RAG Pipeline**: Sentence transformers + Qdrant vector search
- ✅ **Technical Analysis**: RSI, MACD, Bollinger Bands, volatility indicators
- ✅ **Risk Management**: Position limits, volatility checks, sentiment gates
- ✅ **Trade Logging**: Persistent storage with full audit trail

## 🚀 Getting Started

### Prerequisites
-   [Docker Desktop](https://www.docker.com/products/docker-desktop/)
-   [Python 3.10+](https://www.python.org/)
-   [Ollama](https://ollama.com/) (for local LLM inference)
-   Optional: [Kind](https://kind.sigs.k8s.io/) for Kubernetes testing

### 1. Clone the Repository
```bash
git clone https://github.com/shivurj/Cortex5.git
cd Cortex5
```

### 2. Configure Environment
Copy the example environment file and configure settings:

```bash
cp .env.example .env
```

Edit `.env` to configure:
- Database credentials (TimescaleDB)
- Qdrant connection
- NewsAPI key (optional - falls back to Google Finance RSS)
- Risk management parameters

### 3. Pull LLM Model
Ensure you have the Ollama model:
```bash
ollama pull llama3.2:3b
```

### 4. Start Infrastructure
Start the database services using Docker Compose:

```bash
docker-compose up -d
```

This starts:
- TimescaleDB (port 5432)
- Qdrant (port 6333)
- Ollama (port 11434)

### 5. Install Dependencies
Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 6. Initialize Database
Create the TimescaleDB schema (hypertables, indexes, functions):

```bash
python scripts/init_db.py
```

### 7. Ingest News Data (Optional)
Populate Qdrant with financial news for sentiment analysis:

```bash
python scripts/ingest_news.py --tickers AAPL,GOOGL,MSFT --days 7
```

### 8. Run the System
Execute the main script to analyze a ticker:

```bash
python main.py
```

The system will:
1. Fetch market data from Yahoo Finance
2. Analyze sentiment from news articles
3. Calculate technical indicators (RSI, MACD)
4. Validate trade against risk parameters
5. Log execution decision to database

## 📊 Usage Examples

### Analyze a Stock
```bash
python main.py  # Analyzes ticker from message (default: AAPL)
```

### Ingest News for Multiple Tickers
```bash
python scripts/ingest_news.py --tickers AAPL,GOOGL,MSFT,TSLA --days 14
```

### Initialize/Reset Database
```bash
python scripts/init_db.py
```

## ☸️ Kubernetes Setup (Local)
To simulate production deployment using Kind:

1.  **Setup Cluster**:
    ```bash
    ./scripts/setup_cluster.sh
    ```

2.  **Verify Nodes**:
    ```bash
    kubectl get nodes
    ```

## 📂 Project Structure
```
Cortex5/
├── Architecture/              # Design docs and day-wise plans
│   ├── Daywise-Task-Breakdown/
│   │   ├── Day1_Agile_Plan.md
│   │   ├── Day1_Learnings.md
│   │   ├── Day2_Agile_Plan.md
│   │   └── Day2_Learnings.md
│   ├── Architecture.md
│   ├── plan.md
│   └── Vibe_Coding_Plan.md
├── k8s/                       # Kubernetes manifests
│   └── kind-config.yaml
├── scripts/                   # Utility scripts
│   ├── init_db.py            # Database initialization
│   ├── ingest_news.py        # News ingestion pipeline
│   └── setup_cluster.sh      # Kind cluster setup
├── src/
│   ├── agents/               # Agent implementations
│   │   ├── base_agent.py
│   │   ├── data_agent.py     # Market data fetching & storage
│   │   ├── sentiment_agent.py # RAG-based sentiment analysis
│   │   ├── quant_agent.py    # Technical analysis
│   │   ├── risk_agent.py     # Risk validation
│   │   └── execution_agent.py # Trade logging
│   ├── data/                 # Data pipeline components
│   │   ├── market_fetcher.py # Yahoo Finance integration
│   │   ├── validators.py     # Data validation
│   │   ├── db_schema.sql     # TimescaleDB schema
│   │   ├── db_client.py      # TimescaleDB client
│   │   ├── news_fetcher.py   # News API integration
│   │   ├── embeddings.py     # Sentence transformers
│   │   ├── vector_schema.py  # Qdrant schemas
│   │   └── qdrant_client.py  # Qdrant vector store
│   ├── utils/                # Utility functions
│   │   ├── indicators.py     # Technical indicators (RSI, MACD, etc.)
│   │   └── risk_manager.py   # Risk management logic
│   ├── graph.py              # LangGraph definition
│   └── state.py              # Global state schema
├── tests/                    # Test suite (planned)
├── .env.example              # Environment template
├── .gitignore
├── docker-compose.yml        # Local infrastructure
├── main.py                   # Entry point
├── pyproject.toml            # Dependencies
└── README.md
```

## 🔧 Configuration

### Environment Variables
Key configuration options in `.env`:

```bash
# LLM Configuration
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://localhost:11434

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=password

# Vector Store
QDRANT_HOST=localhost
QDRANT_PORT=6333

# News API (optional)
NEWS_API_KEY=your_key_here

# Risk Parameters
MAX_POSITION_PCT=0.10      # Max 10% per position
MAX_VOLATILITY=0.03        # Max 3% daily volatility
MIN_SENTIMENT_SCORE=0.5    # Min sentiment for BUY
```

## 📈 Performance

Typical execution times (M1/M2 Mac):
- Market data fetch (30 days): ~1-2s
- News fetch (10 articles): ~2-3s
- Embedding generation (10 articles): ~1-2s
- Vector search (top-5): <100ms
- Full agent pipeline: ~8-12s

## 🧪 Testing

### Manual Testing
```bash
# 1. Start infrastructure
docker-compose up -d

# 2. Initialize database
python scripts/init_db.py

# 3. Ingest sample data
python scripts/ingest_news.py --tickers AAPL --days 7

# 4. Run analysis
python main.py
```

### Verify Data
```bash
# Check TimescaleDB
docker exec -it cortex5-timescaledb psql -U postgres -d postgres -c \
  "SELECT symbol, timestamp, close FROM market_data ORDER BY timestamp DESC LIMIT 5;"

# Check Qdrant (open browser)
open http://localhost:6333/dashboard
```

## 📚 Documentation

- [Day 1 Learnings](Architecture/Daywise-Task-Breakdown/Day1_Learnings.md) - Foundation setup
- [Day 2 Learnings](Architecture/Daywise-Task-Breakdown/Day2_Learnings.md) - Data pipelines & intelligence
- [Architecture Overview](Architecture/Architecture.md) - System design
- [Implementation Plan](Architecture/plan.md) - Technical blueprint

## 🛣️ Roadmap

### Day 3 (Planned)
- [ ] FastAPI backend with WebSocket support
- [ ] Next.js dashboard for monitoring
- [ ] Backtesting framework
- [ ] Performance metrics (Sharpe ratio, drawdown)

### Future
- [ ] Production deployment (AWS EKS)
- [ ] CI/CD pipeline
- [ ] Prometheus + Grafana monitoring
- [ ] Paper trading mode
- [ ] Strategy optimization

## 🤝 Contributing
1.  Fork the repository
2.  Create your feature branch (`git checkout -b feature/amazing-feature`)
3.  Commit your changes (`git commit -m 'Add some amazing feature'`)
4.  Push to the branch (`git push origin feature/amazing-feature`)
5.  Open a Pull Request

## 📄 License
This project is for educational purposes.

## 🙏 Acknowledgments
- LangChain & LangGraph teams
- Ollama for local LLM inference
- TimescaleDB & Qdrant communities
