-- TimescaleDB Schema for Cortex5 AI Hedge Fund
-- This schema defines tables for market data and trade execution logs

-- Enable TimescaleDB extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================================
-- Table: market_data
-- Purpose: Store OHLCV (Open, High, Low, Close, Volume) time-series data
-- ============================================================================

CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL,
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open NUMERIC(12, 2) NOT NULL,
    high NUMERIC(12, 2) NOT NULL,
    low NUMERIC(12, 2) NOT NULL,
    close NUMERIC(12, 2) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (symbol, timestamp)
);

-- Convert to hypertable (partitioned by time)
-- This enables TimescaleDB's time-series optimizations
SELECT create_hypertable(
    'market_data',
    'timestamp',
    if_not_exists => TRUE,
    migrate_data => TRUE
);

-- Create index for efficient symbol-based queries
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_time 
    ON market_data (symbol, timestamp DESC);

-- Create index for time-range queries
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp 
    ON market_data (timestamp DESC);

-- ============================================================================
-- Table: trade_logs
-- Purpose: Store trade execution records and order history
-- ============================================================================

CREATE TABLE IF NOT EXISTS trade_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    symbol VARCHAR(10) NOT NULL,
    side VARCHAR(4) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price NUMERIC(12, 2) NOT NULL CHECK (price > 0),
    total_value NUMERIC(15, 2) GENERATED ALWAYS AS (quantity * price) STORED,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    sentiment_score NUMERIC(3, 2),
    trade_signal VARCHAR(10),
    risk_approved BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for efficient symbol-based trade queries
CREATE INDEX IF NOT EXISTS idx_trade_logs_symbol 
    ON trade_logs (symbol, timestamp DESC);

-- Create index for status filtering
CREATE INDEX IF NOT EXISTS idx_trade_logs_status 
    ON trade_logs (status, timestamp DESC);

-- Create index for time-range queries
CREATE INDEX IF NOT EXISTS idx_trade_logs_timestamp 
    ON trade_logs (timestamp DESC);

-- ============================================================================
-- Table: portfolio_state
-- Purpose: Track current portfolio holdings and cash balance
-- ============================================================================

CREATE TABLE IF NOT EXISTS portfolio_state (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    average_cost NUMERIC(12, 2) NOT NULL DEFAULT 0,
    current_value NUMERIC(15, 2),
    unrealized_pnl NUMERIC(15, 2),
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for symbol lookups
CREATE INDEX IF NOT EXISTS idx_portfolio_symbol 
    ON portfolio_state (symbol);

-- ============================================================================
-- Table: cash_balance
-- Purpose: Track available cash for trading
-- ============================================================================

CREATE TABLE IF NOT EXISTS cash_balance (
    id SERIAL PRIMARY KEY,
    balance NUMERIC(15, 2) NOT NULL DEFAULT 100000.00,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Insert initial cash balance if not exists
INSERT INTO cash_balance (balance) 
SELECT 100000.00
WHERE NOT EXISTS (SELECT 1 FROM cash_balance);

-- ============================================================================
-- Continuous Aggregates (for performance optimization)
-- Purpose: Pre-compute daily statistics for faster queries
-- ============================================================================

-- Daily OHLCV summary (useful for backtesting and analytics)
CREATE MATERIALIZED VIEW IF NOT EXISTS market_data_daily
WITH (timescaledb.continuous) AS
SELECT
    symbol,
    time_bucket('1 day', timestamp) AS day,
    first(open, timestamp) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, timestamp) AS close,
    sum(volume) AS volume,
    count(*) AS num_records
FROM market_data
GROUP BY symbol, day
WITH NO DATA;

-- Refresh policy for continuous aggregate (refresh every hour)
SELECT add_continuous_aggregate_policy(
    'market_data_daily',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Function to get latest price for a symbol
CREATE OR REPLACE FUNCTION get_latest_price(ticker VARCHAR)
RETURNS NUMERIC AS $$
    SELECT close 
    FROM market_data 
    WHERE symbol = ticker 
    ORDER BY timestamp DESC 
    LIMIT 1;
$$ LANGUAGE SQL;

-- Function to calculate portfolio total value
CREATE OR REPLACE FUNCTION get_portfolio_value()
RETURNS NUMERIC AS $$
    SELECT 
        COALESCE(SUM(quantity * get_latest_price(symbol)), 0) + 
        (SELECT balance FROM cash_balance LIMIT 1)
    FROM portfolio_state
    WHERE quantity > 0;
$$ LANGUAGE SQL;

-- ============================================================================
-- Data Retention Policy (optional - uncomment to enable)
-- Purpose: Automatically drop old data to save space
-- ============================================================================

-- Drop market data older than 2 years
-- SELECT add_retention_policy('market_data', INTERVAL '2 years', if_not_exists => TRUE);

-- ============================================================================
-- Grants (adjust based on your user setup)
-- ============================================================================

-- Grant permissions to postgres user (adjust as needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
