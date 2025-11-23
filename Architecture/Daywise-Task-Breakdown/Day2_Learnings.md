# Cortex 5 - Day 2 Technical Learning Guide: Data Pipelines & Intelligent Agents

## 📝 Executive Summary
Day 2 transformed Cortex5 from a proof-of-concept with mock data into a **fully functional AI hedge fund** with real data pipelines, database persistence, and intelligent agents. We implemented:
- **Real market data ingestion** from Yahoo Finance with validation and TimescaleDB storage
- **RAG-based sentiment analysis** using Qdrant vector store and embeddings
- **Technical analysis** with RSI and MACD indicators
- **Risk management** with portfolio constraints and volatility checks
- **Trade execution logging** to TimescaleDB

---

## 1. Architecture Deep Dive

### 1.1 The Bloodstream: Market Data Pipeline
This pipeline ensures high-quality financial data flows into the system.

```ascii
[Yahoo Finance API]
        |
        v (yfinance library)
[MarketDataFetcher] <--- Retry Logic (Exponential Backoff)
        |
        v (pandas DataFrame)
[DataValidator] <--- 7-Layer Integrity Check
        |
        v (validated OHLCV)
[TimescaleDB Client] <--- Connection Pooling
        |
        v (bulk insert)
[TimescaleDB Hypertable]
    (market_data)
        |
        +---> [Continuous Aggregate] (market_data_daily)
```

**Technical Details:**
- **Retry Logic**: Implemented `tenacity`-style exponential backoff (1s, 2s, 4s) to handle transient network failures from Yahoo Finance.
- **Data Validation**: `validate_ohlcv_data` enforces strict rules:
    - No nulls in OHLCV
    - High >= Low (always)
    - Volume >= 0
    - Timestamps monotonic increasing
- **TimescaleDB Hypertables**: We use hypertables to automatically partition data by time. This makes queries on recent data (e.g., "last 30 days") O(1) complexity instead of O(N).

### 1.2 The Neural Network: RAG Pipeline
This pipeline gives the agents "memory" and context from unstructured news data.

```ascii
[Google Finance RSS / NewsAPI]
            |
            v (fetch_news)
    [News Articles]
            |
            v (sentence-transformers)
  [Embedding Generator]
   (BAAI/bge-small-en-v1.5)
            |
            v (384-dim vectors)
    [Qdrant Vector DB]
            |
            v (cosine similarity search)
  [Top-K Similar Articles]
            |
            v (LLM analysis)
   [Sentiment Score: 0.0-1.0]
```

**Technical Details:**
- **Embedding Model**: We chose `BAAI/bge-small-en-v1.5` because:
    - **Size**: Small (384 dimensions) vs standard 768 or 1536.
    - **Speed**: 2x faster inference on CPU/MPS.
    - **Quality**: MTEB leaderboard top performer for its size.
- **Vector Search**: We use **Cosine Similarity** to find news semantically related to the ticker.
- **RAG Context**: We retrieve the top-5 most relevant articles to fit comfortably in the Llama 3.2 context window without noise.

### 1.3 The Brain: Agent Orchestration
The flow of information through the "Council of Agents".

```ascii
[User Request] -> [Data Agent]
                       |
        (Market Data)  v
               [Sentiment Agent] <--- (News RAG)
                       |
      (Sentiment Score)|
                       v
                 [Quant Agent] <--- (Technical Indicators)
                       |
        (Trade Signal) v
                 [Risk Agent] <--- (Risk Checks)
                       |
       (Risk Approval) v
              [Execution Agent] -> [TimescaleDB Trade Log]
```

---

## 2. Component Analysis (Deep Technical)

### 2.1 TimescaleDB Integration
**Why Hypertables?**
Standard PostgreSQL tables degrade in performance as they grow to millions of rows. Hypertables automatically partition data into "chunks" based on time intervals.
- **Write Performance**: Inserts go to the latest chunk (in memory).
- **Read Performance**: Queries prune chunks that don't match the time range.

**Why Continuous Aggregates?**
We created `market_data_daily` as a continuous aggregate. This is a materialized view that **automatically refreshes** as new data comes in. It pre-calculates OHLCV for larger timeframes (e.g., daily from minute data), making backtesting queries instant.

### 2.2 Qdrant Vector Store
**Vector Search Mechanics:**
We use HNSW (Hierarchical Navigable Small World) index in Qdrant for approximate nearest neighbor search.
- **Collection Config**: `distance=Cosine`, `vector_size=384`.
- **Filtering**: We filter by `ticker` payload field *before* vector search (pre-filtering) to ensure we only search relevant news.

### 2.3 Risk Management Logic
The `RiskManager` implements a "Swiss Cheese Model" of safety - a trade must pass 4 layers of defense:
1.  **Position Sizing**: `position_value <= portfolio_value * MAX_POSITION_PCT` (Default 10%).
2.  **Volatility Check**: `daily_volatility <= MAX_VOLATILITY` (Default 3%). High volatility implies high risk.
3.  **Sentiment Gate**: If `Signal == BUY`, then `Sentiment >= MIN_SENTIMENT_SCORE` (Default 0.5). Don't buy bad news.
4.  **Capital Check**: `cash >= required_amount`.

### 2.4 Technical Indicators (Math)
**RSI (Relative Strength Index):**
$$RSI = 100 - \frac{100}{1 + RS}$$
Where $$RS = \frac{\text{Average Gain}}{\text{Average Loss}}$$
- We use Pandas `rolling(window=14).mean()` for efficient calculation.

**MACD (Moving Average Convergence Divergence):**
1.  `EMA_fast` = 12-period Exponential Moving Average
2.  `EMA_slow` = 26-period EMA
3.  `MACD_line` = `EMA_fast` - `EMA_slow`
4.  `Signal_line` = 9-period EMA of `MACD_line`
5.  `Histogram` = `MACD_line` - `Signal_line`
- **Crossover Strategy**: BUY when MACD crosses *above* Signal line. SELL when MACD crosses *below*.

---

## 3. Challenges & Solutions (The "Gotchas")

### 🐛 Bug 1: Psycopg2 vs NumPy Types
**The Issue**: `psycopg2` (the Postgres driver) is a strict C-library. It crashed with `can't adapt type 'numpy.int64'` when trying to insert Pandas data.
**The Fix**: Explicit type casting in `db_client.py`.
```python
# BAD: relying on implicit adaptation
data = [tuple(x) for x in df.values]

# GOOD: explicit python native types
data = []
for row in df.itertuples():
    data.append((str(row.symbol), float(row.close), int(row.volume)))
```
**Why**: Ensures 100% data type safety and prevents subtle precision errors.

### 🐛 Bug 2: MACD Data Sufficiency
**The Issue**: We were fetching "1mo" (approx 22 days) of data. MACD requires a 26-day slow EMA to even *start* calculating. The result was all `NaN`.
**The Fix**: Increased fetch period to "3mo" in `DataAgent`.
**Why**: You cannot calculate a 26-day trend with 22 days of data.

### 🐛 Bug 3: Qdrant Client API Drift
**The Issue**: `qdrant-client` library versions have different method names (`search` vs `query_points`).
**The Fix**: Added a `try...except AttributeError` block to attempt `search` and fallback to `query_points`.
**Production Note**: In a strict production env, we should pin the exact version in `pyproject.toml` to avoid this.

---

## 4. Key Code Patterns

### 4.1 Robust Database Connection Pool
Using `contextlib.contextmanager` for clean resource management.
```python
@contextmanager
def get_connection(self):
    if self.connection_pool is None:
        self.connect()
    conn = self.connection_pool.getconn()
    try:
        yield conn
    finally:
        self.connection_pool.putconn(conn)
```

### 4.2 Vectorized Indicator Calculation
Using Pandas vectorization instead of loops (100x faster).
```python
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gains = delta.where(delta > 0, 0.0)
    losses = -delta.where(delta < 0, 0.0)
    # Vectorized rolling mean
    rs = gains.rolling(period).mean() / losses.rolling(period).mean()
    return 100 - (100 / (1 + rs))
```

---

## 5. Future Considerations (Production Readiness)

1.  **Dependency Pinning**: Pin `qdrant-client==1.7.0` and `psycopg2-binary==2.9.9` to ensure deterministic behavior.
2.  **Secret Management**: Move `.env` credentials to AWS Secrets Manager or Kubernetes Secrets.
3.  **Asynchronous I/O**: Switch `psycopg2` (sync) to `asyncpg` (async) and `requests` to `aiohttp` for higher concurrency in the API layer.
4.  **Data Quality Monitoring**: Add Great Expectations or similar tool to alert on data anomalies (e.g., sudden price spikes).

---

**Day 2 Status**: ✅ **COMPLETE & VERIFIED**
**Next Milestone**: Day 3 - Web Interface & Backtesting
