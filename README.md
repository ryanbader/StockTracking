# Stock Market Signal Tracker

A Python + DuckDB project that ingests weekly adjusted stock data, calculates rolling market signals, and backtests mean-reversion strategies across 135+ equities and ETFs.

This project was built to demonstrate a repeatable analytics workflow: automated data ingestion, local database storage, SQL-based feature engineering, strategy backtesting, and interactive analysis in JupyterLab.

---

## Overview

The scanner tracks weekly OHLCV data from the Alpha Vantage API and analyzes whether extreme price deviations have historically led to profitable forward returns.

The project focuses on:

- Weekly adjusted stock data
- Rolling z-score signals
- Adjusted high / low deviation signals
- Mean-reversion backtesting
- Volatility regime analysis
- Interactive Plotly visualizations
- Automated daily data refreshes using Windows Task Scheduler

---

## Tech Stack

- Python
- DuckDB
- SQL
- Pandas
- Plotly
- JupyterLab
- Alpha Vantage API# Stock Market Signal Tracker

# Quantitative Market Signal Scanner

A Python + DuckDB project that ingests weekly adjusted stock data, calculates rolling market signals, and backtests mean-reversion strategies across 135+ equities and ETFs.

This project was built to demonstrate a repeatable analytics workflow: automated data ingestion, local database storage, SQL-based feature engineering, strategy backtesting, and interactive analysis in JupyterLab.

---

## Overview

The scanner tracks weekly OHLCV data from the Alpha Vantage API and analyzes whether extreme price deviations have historically led to profitable forward returns.

The project focuses on:

- Weekly adjusted stock data
- Rolling z-score signals
- Adjusted high / low deviation signals
- Mean-reversion backtesting
- Volatility regime analysis
- Interactive Plotly visualizations
- Automated daily data refreshes using Windows Task Scheduler

---

## Tech Stack

- Python
- DuckDB
- SQL
- Pandas
- Plotly
- JupyterLab
- Alpha Vantage API
- Windows Task Scheduler

---

## Key Features

### Automated Data Pipeline

The `update_prices.py` script pulls weekly adjusted data from Alpha Vantage and stores it in DuckDB.

The pipeline:

- Fetches weekly adjusted OHLCV data
- Converts API responses into clean pandas DataFrames
- Uses DuckDB `MERGE` logic to insert or update rows
- Rotates through symbol batches to stay within free API limits
- Can run automatically once per day through Windows Task Scheduler

### Local DuckDB Storage

Market data is stored locally in a DuckDB database, making the project lightweight, portable, and easy to query with SQL.

DuckDB is used to:

- Store adjusted weekly price history
- Query large datasets efficiently
- Build rolling market features
- Join signal tables with forward return data
- Support repeatable analysis without relying on spreadsheets

### SQL-Based Feature Engineering

The project uses SQL queries to calculate historical signal metrics directly from the database.

Signals include:

- Rolling moving averages
- Rolling standard deviations
- Rolling z-scores
- Price deviation from adjusted highs
- Price deviation from adjusted lows
- Forward returns over multiple time horizons
- Volatility regime classifications

This approach keeps the analytical logic transparent and reproducible.

### Mean-Reversion Signal Testing

The scanner evaluates whether unusually large price moves have historically been followed by positive or negative forward returns.

Example signal questions include:

- What happens after a stock trades far below its rolling average?
- Do extreme negative z-scores tend to mean-revert?
- Are adjusted low deviations useful entry signals?
- Do results improve during certain volatility regimes?
- Which symbols have shown the strongest historical signal behavior?

### Backtesting Workflow

The backtesting process compares signal events against future returns.

The analysis can evaluate:

- Average forward return after a signal
- Median forward return after a signal
- Win rate
- Number of historical signal events
- Best and worst forward returns
- Performance by symbol
- Performance by sector or ETF group
- Performance by volatility regime

The goal is not to predict future prices with certainty, but to identify historical patterns that may be worth further research.

### Interactive JupyterLab Analysis

The project includes notebook-based analysis using pandas and Plotly.

Interactive charts can be used to explore:

- Price history
- Rolling z-score behavior
- Signal event timing
- Forward return distributions
- Symbol-level comparisons
- Volatility regime changes
- Backtest summary results

This makes the project useful for both systematic research and visual market review.

---
