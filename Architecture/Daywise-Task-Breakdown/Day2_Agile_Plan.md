# Cortex5 - Day 2: Data Pipelines & Agent Intelligence
## Methodology: Agile Scrum (Epics > Stories > Tasks)
**Goal**: Implement real data pipelines, integrate databases (TimescaleDB & Qdrant), and enhance agent intelligence with actual tools and logic.

---

## 📊 Progress Tracker
*(Update this section as you complete tasks using the Vibe Coding workflow)*

- [x] **Epic 1: Data Pipeline - The Bloodstream**
    - [x] Story 1.1: Market Data Ingestion
    - [x] Story 1.2: TimescaleDB Schema & Integration
- [x] **Epic 2: Memory & Context - The Neural Network**
    - [x] Story 2.1: News Ingestion & Embedding
    - [x] Story 2.2: Qdrant Vector Store Integration
- [x] **Epic 3: Agent Intelligence - The Brain Upgrade**
    - [x] Story 3.1: Data Agent Real Tools
    - [x] Story 3.2: Sentiment Agent RAG Implementation
    - [x] Story 3.3: Quant Agent Technical Indicators
    - [x] Story 3.4: Risk Agent Portfolio Logic
- [ ] **Epic 4: Validation & Testing**
    - [ ] Story 4.1: End-to-End Testing
    - [ ] Story 4.2: Performance Verification

---

## 🌊 Epic 1: Data Pipeline - The Bloodstream
**Objective**: Build the data ingestion pipeline to fetch real market data and store it in TimescaleDB.

### Story 1.1: Market Data Ingestion
**Description**: Create a robust data fetcher that pulls OHLCV data from Yahoo Finance.

*   **Task 1.1.1**: Implement Yahoo Finance Data Fetcher. [x]
    *   **Agent Prompt**:
        > "Act as a Senior Data Engineer. Create `src/data/market_fetcher.py`. Implement a class `MarketDataFetcher` with a method `fetch_ohlcv(ticker: str, period: str = '1mo', interval: str = '1d')` using `yfinance`. The method should return a pandas DataFrame with columns: `timestamp`, `open`, `high`, `low`, `close`, `volume`. Add error handling for invalid tickers and network failures. Include retry logic with exponential backoff."

*   **Task 1.1.2**: Create Data Validation Layer. [x]
    *   **Agent Prompt**:
        > "Create `src/data/validators.py`. Implement a `validate_ohlcv_data(df: pd.DataFrame) -> bool` function that checks:
        > 1. No null values in critical columns (open, high, low, close).
        > 2. High >= Low for all rows.
        > 3. Volume is non-negative.
        > 4. Timestamps are in ascending order.
        > Return True if valid, raise `DataValidationError` otherwise."

### Story 1.2: TimescaleDB Schema & Integration
**Description**: Define the database schema and create integration layer for TimescaleDB.

*   **Task 1.2.1**: Define TimescaleDB Schema. [x]
    *   **Agent Prompt**:
        > "Create `src/data/db_schema.sql`. Define a table `market_data` with columns:
        > - `id` (SERIAL PRIMARY KEY)
        > - `symbol` (VARCHAR(10) NOT NULL)
        > - `timestamp` (TIMESTAMPTZ NOT NULL)
        > - `open` (NUMERIC(12,2))
        > - `high` (NUMERIC(12,2))
        > - `low` (NUMERIC(12,2))
        > - `close` (NUMERIC(12,2))
        > - `volume` (BIGINT)
        > Create a hypertable on `market_data` partitioned by `timestamp`.
        > Add an index on `(symbol, timestamp DESC)` for efficient queries.
        > Also create a `trade_logs` table with: `id`, `timestamp`, `symbol`, `side` (BUY/SELL), `quantity`, `price`, `status`."

*   **Task 1.2.2**: Implement Database Client. [x]
    *   **Agent Prompt**:
        > "Create `src/data/db_client.py`. Implement a class `TimescaleDBClient` using `psycopg2` or `asyncpg`. Include methods:
        > - `connect()`: Establish connection using env vars (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD).
        > - `insert_market_data(df: pd.DataFrame)`: Bulk insert OHLCV data.
        > - `query_market_data(symbol: str, start_date: datetime, end_date: datetime)`: Fetch data for a symbol.
        > - `log_trade(symbol, side, quantity, price, status)`: Insert trade execution record.
        > Use connection pooling and implement proper error handling."

*   **Task 1.2.3**: Create Database Initialization Script. [x]
    *   **Agent Prompt**:
        > "Create `scripts/init_db.py`. This script should:
        > 1. Read the schema from `src/data/db_schema.sql`.
        > 2. Connect to TimescaleDB using the `TimescaleDBClient`.
        > 3. Execute the schema creation statements.
        > 4. Verify the hypertable was created successfully.
        > 5. Print confirmation message.
        > Make it idempotent (safe to run multiple times)."

---

## 🧠 Epic 2: Memory & Context - The Neural Network
**Objective**: Build the RAG (Retrieval Augmented Generation) pipeline for sentiment analysis using Qdrant.

### Story 2.1: News Ingestion & Embedding
**Description**: Create a pipeline to fetch financial news and generate embeddings.

*   **Task 2.1.1**: Implement News Fetcher. [x]
    *   **Agent Prompt**:
        > "Create `src/data/news_fetcher.py`. Implement a class `NewsFetcher` with method `fetch_news(ticker: str, days_back: int = 7)`. Use a free API like:
        > - NewsAPI (newsapi.org) - requires API key
        > - Or scrape Google Finance RSS feeds
        > Return a list of dictionaries with: `title`, `description`, `published_at`, `url`, `source`.
        > Handle rate limiting and add caching to avoid redundant API calls."

*   **Task 2.1.2**: Create Embedding Generator. [x]
    *   **Agent Prompt**:
        > "Create `src/data/embeddings.py`. Implement a class `EmbeddingGenerator` using `sentence-transformers` library with model `BAAI/bge-small-en-v1.5` (lightweight, 384 dimensions).
        > Methods:
        > - `generate_embedding(text: str) -> List[float]`: Generate embedding for a single text.
        > - `batch_generate(texts: List[str]) -> List[List[float]]`: Generate embeddings in batch for efficiency.
        > Use GPU if available, otherwise CPU. Add proper error handling."

### Story 2.2: Qdrant Vector Store Integration
**Description**: Set up Qdrant collections and implement vector search.

*   **Task 2.2.1**: Define Qdrant Schema. [x]
    *   **Agent Prompt**:
        > "Create `src/data/vector_schema.py`. Define a Pydantic model `NewsDocument` with fields:
        > - `id` (str)
        > - `ticker` (str)
        > - `title` (str)
        > - `content` (str)
        > - `published_at` (datetime)
        > - `source` (str)
        > - `sentiment_label` (Optional[str]) - 'positive', 'negative', 'neutral'
        > - `embedding` (List[float])
        > This will be the payload structure for Qdrant."

*   **Task 2.2.2**: Implement Qdrant Client. [x]
    *   **Agent Prompt**:
        > "Create `src/data/qdrant_client.py`. Implement a class `QdrantVectorStore` using `qdrant-client`. Methods:
        > - `create_collection(collection_name: str, vector_size: int = 384)`: Create collection with cosine similarity.
        > - `upsert_documents(documents: List[NewsDocument])`: Insert/update documents.
        > - `search_similar(query_text: str, ticker: str, top_k: int = 5)`: Find similar news articles.
        > - `get_collection_info()`: Return stats about the collection.
        > Use the Qdrant service from docker-compose (localhost:6333)."

*   **Task 2.2.3**: Create News Ingestion Pipeline. [x]
    *   **Agent Prompt**:
        > "Create `scripts/ingest_news.py`. This script orchestrates:
        > 1. Fetch news for a list of tickers (e.g., ['AAPL', 'GOOGL', 'MSFT']).
        > 2. Generate embeddings for each article.
        > 3. Store in Qdrant with proper metadata.
        > 4. Log the number of articles processed.
        > Make it runnable as: `python scripts/ingest_news.py --tickers AAPL,GOOGL --days 7`"

---

## 🎯 Epic 3: Agent Intelligence - The Brain Upgrade
**Objective**: Replace mock tools with real implementations in all agents.

### Story 3.1: Data Agent Real Tools
**Description**: Connect the Data Agent to TimescaleDB and Yahoo Finance.

*   **Task 3.1.1**: Implement Data Agent Tools. [x]
    *   **Agent Prompt**:
        > "Update `src/agents/data_agent.py`. Replace the mock tool with real implementation:
        > 1. Create a tool `fetch_stock_data` that uses `MarketDataFetcher` to get OHLCV data.
        > 2. Store the fetched data in TimescaleDB using `TimescaleDBClient`.
        > 3. Update the agent's `run()` method to populate `state['market_data']` with the fetched DataFrame.
        > 4. Add logging to track what data was fetched.
        > The agent should handle cases where data already exists in DB (check before fetching)."

### Story 3.2: Sentiment Agent RAG Implementation
**Description**: Implement RAG-based sentiment analysis using Qdrant.

*   **Task 3.2.1**: Implement Sentiment Analysis Tool. [x]
    *   **Agent Prompt**:
        > "Update `src/agents/sentiment_agent.py`. Implement:
        > 1. Tool `query_news_vectors`: Use `QdrantVectorStore` to find similar news for the ticker.
        > 2. Tool `analyze_sentiment`: Pass retrieved news to the LLM with a prompt:
        >    'Based on these news headlines about {ticker}, provide a sentiment score from 0.0 (very bearish) to 1.0 (very bullish). Consider market impact, tone, and relevance.'
        > 3. Update `state['sentiment_score']` with the LLM's output (parsed as float).
        > 4. If no news found, default to 0.5 (neutral)."

### Story 3.3: Quant Agent Technical Indicators
**Description**: Implement real technical analysis calculations.

*   **Task 3.3.1**: Create Technical Indicators Library. [x]
    *   **Agent Prompt**:
        > "Create `src/utils/indicators.py`. Implement functions using `pandas` and `numpy`:
        > - `calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series`: Relative Strength Index.
        > - `calculate_macd(prices: pd.Series) -> Dict`: MACD line, Signal line, Histogram.
        > - `calculate_bollinger_bands(prices: pd.Series, period: int = 20) -> Dict`: Upper, Middle, Lower bands.
        > - `calculate_moving_average(prices: pd.Series, period: int) -> pd.Series`: Simple Moving Average.
        > Add docstrings with formulas and return types."

*   **Task 3.3.2**: Update Quant Agent Logic. [x]
    *   **Agent Prompt**:
        > "Update `src/agents/quant_agent.py`. Implement trading logic:
        > 1. Extract `close` prices from `state['market_data']`.
        > 2. Calculate RSI and MACD using the indicators library.
        > 3. Implement strategy:
        >    - BUY if: RSI < 30 (oversold) AND MACD crosses above signal line.
        >    - SELL if: RSI > 70 (overbought) AND MACD crosses below signal line.
        >    - HOLD otherwise.
        > 4. Update `state['trade_signal']` with the decision.
        > 5. Add reasoning to `state['messages']` explaining the decision."

### Story 3.4: Risk Agent Portfolio Logic
**Description**: Implement real risk management rules.

*   **Task 3.4.1**: Create Risk Management Module. [x]
    *   **Agent Prompt**:
        > "Create `src/utils/risk_manager.py`. Implement a class `RiskManager` with:
        > - `check_position_size(signal, current_portfolio, max_position_pct=0.1)`: Ensure no single position exceeds 10% of portfolio.
        > - `check_volatility(market_data, max_volatility=0.03)`: Calculate daily volatility, reject if > 3%.
        > - `check_sentiment_threshold(sentiment_score, signal)`: For BUY, require sentiment >= 0.5.
        > - `approve_trade(state) -> bool`: Aggregate all checks and return approval decision."

*   **Task 3.4.2**: Update Risk Agent. [x]
    *   **Agent Prompt**:
        > "Update `src/agents/risk_agent.py`. Use `RiskManager` to validate trades:
        > 1. Instantiate `RiskManager` with portfolio config (can be hardcoded for now: $100,000 starting capital).
        > 2. Call `approve_trade(state)` to get approval decision.
        > 3. Update `state['risk_approval']` with the result.
        > 4. If rejected, add a message explaining which risk check failed."

---

## ✅ Epic 4: Validation & Testing
**Objective**: Ensure the entire system works end-to-end with real data.

### Story 4.1: End-to-End Testing
**Description**: Test the complete agent workflow with real market data.

*   **Task 4.1.1**: Create Integration Test Script. [ ]
    *   **Agent Prompt**:
        > "Create `tests/test_integration.py`. Implement a test that:
        > 1. Starts with a clean database state.
        > 2. Ingests market data for AAPL (last 30 days).
        > 3. Ingests news for AAPL.
        > 4. Runs the agent graph with initial state requesting analysis of AAPL.
        > 5. Asserts that:
        >    - `market_data` is populated.
        >    - `sentiment_score` is between 0.0 and 1.0.
        >    - `trade_signal` is one of BUY/SELL/HOLD.
        >    - `execution_status` is updated.
        > Use `pytest` framework."

*   **Task 4.1.2**: Create Manual Testing Guide. [ ]
    *   **Agent Prompt**:
        > "Create `docs/testing_guide.md`. Document:
        > 1. How to start the infrastructure (`docker-compose up`).
        > 2. How to initialize the database (`python scripts/init_db.py`).
        > 3. How to ingest sample data (`python scripts/ingest_news.py --tickers AAPL --days 7`).
        > 4. How to run the main application (`python main.py`).
        > 5. Expected output at each step.
        > 6. How to verify data in TimescaleDB and Qdrant using SQL and Qdrant dashboard."

### Story 4.2: Performance Verification
**Description**: Measure and optimize system performance.

*   **Task 4.2.1**: Add Performance Logging. [ ]
    *   **Agent Prompt**:
        > "Update `src/agents/base_agent.py`. Add timing decorators:
        > 1. Measure execution time for each agent's `run()` method.
        > 2. Log to console: `[AgentName] completed in X.XX seconds`.
        > 3. Track total graph execution time in `main.py`.
        > Use Python's `time.perf_counter()` for precision."

*   **Task 4.2.2**: Create Performance Benchmarks. [ ]
    *   **Agent Prompt**:
        > "Create `tests/test_performance.py`. Benchmark:
        > 1. Data fetching speed (100 days of AAPL data).
        > 2. Embedding generation speed (100 news articles).
        > 3. Vector search latency (query with top_k=10).
        > 4. Full graph execution time (single ticker analysis).
        > Assert that each operation completes within reasonable thresholds (e.g., graph < 10 seconds)."

---

## 🔗 Enhanced Orchestration (End of Day 2)

*   **Task 5.0**: Update Main Entry Point. [ ]
    *   **Agent Prompt**:
        > "Update `main.py` to:
        > 1. Accept command-line arguments: `--ticker AAPL --action analyze`.
        > 2. Check if data exists in DB, if not, trigger ingestion.
        > 3. Run the agent graph.
        > 4. Pretty-print the final decision with colors (use `rich` library).
        > 5. Optionally save the execution trace to a JSON file for debugging."

---

## 📝 Definition of Done (Day 2)
1.  TimescaleDB contains real OHLCV data for at least 3 tickers (AAPL, GOOGL, MSFT). [ ]
2.  Qdrant contains embedded news articles for the same tickers. [ ]
3.  Data Agent fetches and stores data from Yahoo Finance. [ ]
4.  Sentiment Agent performs RAG-based sentiment analysis using Qdrant. [ ]
5.  Quant Agent calculates RSI and MACD and generates valid trade signals. [ ]
6.  Risk Agent applies real risk checks (volatility, sentiment, position size). [ ]
7.  Execution Agent logs trades to TimescaleDB. [ ]
8.  Integration test passes successfully. [ ]
9.  Full graph execution completes in < 15 seconds for a single ticker. [ ]
10. Documentation (`testing_guide.md`) is complete and verified. [ ]

---

## 🚀 Bonus Tasks (If Time Permits)
- [ ] Add a simple CLI dashboard using `rich` to show agent status in real-time.
- [ ] Implement caching for market data to avoid redundant API calls.
- [ ] Add Prometheus metrics endpoints for monitoring.
- [ ] Create a simple FastAPI endpoint to trigger analysis via HTTP.
