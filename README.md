# Stock Market Signal Tracker

A Python, DuckDB, SQL, and Plotly project that ingests weekly adjusted stock market data, calculates rolling market signals, and backtests mean-reversion strategies across large-cap equities, ETFs, and selected high-volatility tickers.

This project was built as a repeatable market research workflow: collect data, store it locally, calculate indicators with SQL, test signal performance, and visualize results in JupyterLab.

---

## Project Overview

The Quantitative Market Signal Scanner analyzes weekly stock behavior across a rotating universe of 135+ symbols, including top SPY holdings, ETFs, and selected individual stocks.

The project uses Alpha Vantage weekly adjusted data to track OHLCV history and evaluate whether extreme price deviations historically led to profitable forward returns.

The main goal is to identify whether z-score based signals can help surface potential trading opportunities, especially mean-reversion setups after large downside moves.

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

### Automated Weekly Data Pipeline

The project includes a Python ingestion script that pulls weekly adjusted stock data from the Alpha Vantage API and stores it locally in DuckDB.

The pipeline:

- Pulls weekly adjusted OHLCV data
- Converts raw API responses into clean pandas DataFrames
- Stores data in a DuckDB table
- Uses SQL `MERGE` logic to update existing rows and insert new rows
- Rotates through symbol batches to work within free API request limits
- Can be scheduled to run automatically with Windows Task Scheduler

Because Alpha Vantage's free tier limits daily API requests, the script rotates through a fixed batch of symbols each day instead of refreshing the full universe at once.

---

## DuckDB Storage Layer

Market data is stored locally in DuckDB using a structured schema:

```sql
symbol
week_date
open
high
low
close
adjusted_close
volume
dividend_amount

DuckDB was used because it provides fast analytical queries, SQL window functions, and simple integration with Python and JupyterLab.

Rolling Z-Score Analysis

The project calculates rolling z-scores to measure how far a stock is trading from its recent average.

z_score = (adjusted_close - rolling_mean) / rolling_std

This helps identify unusually stretched conditions such as:

z_score <= -2.5  → potential downside mean-reversion setup
z_score >= 2.5   → potential upside extension

The analysis includes:

Adjusted close z-score
Adjusted high z-score
Adjusted low z-score
Maximum absolute z-score
Latest-week signal scanner tables
Adjusted High and Low Signals

To avoid mixing raw high/low prices with adjusted close values, the project adjusts weekly high and low values onto the same scale as adjusted close.

adjusted_high = high * (adjusted_close / close)
adjusted_low  = low  * (adjusted_close / close)

This is especially important for stocks with historical splits, where raw highs and lows can distort z-score calculations.

Mean-Reversion Backtesting

The notebook backtests whether extreme z-score events historically led to positive forward returns.

Example strategy logic:

If z_score <= -threshold → buy signal
If z_score >= threshold  → sell signal

The backtest calculates:

Forward return
Strategy return
Average return
Median return
Win rate
Total strategy return
Best trade
Worst trade

The strategy can be tested across:

Multiple z-score thresholds
Multiple holding periods
Close-based signals
Adjusted high/low signals
Consecutive extreme-week signals
Consecutive Extreme-Week Testing

The project also tests whether a signal becomes more useful after remaining extreme for multiple weeks.

Example:

Enter only when adjusted close z-score stays below -2.5 for 2 consecutive weeks.

This helps compare one-week extreme events against more persistent deviation regimes.

Volatility Regime Analysis

The project also explores volatility using weekly returns instead of price levels.

weekly_return = adjusted_close / previous_adjusted_close - 1
vol_20w = rolling standard deviation of weekly returns
vol_52w = longer-term rolling volatility
vol_ratio = vol_20w / vol_52w

This helps distinguish between:

Normal pullbacks
Elevated-volatility breakdowns
Potentially cleaner mean-reversion setups
Example Research Questions

This project is designed to answer questions such as:

Which stocks are currently trading at extreme weekly z-scores?
Do downside z-score events historically produce positive forward returns?
Are buy signals more reliable than sell signals?
Does requiring two consecutive extreme weeks improve signal quality?
Do adjusted high/low z-score signals trigger more frequently than close-based signals?
Does volatility regime affect signal performance?
Which symbols show the strongest mean-reversion tendencies?
Current Insights

Early analysis suggests that downside deviation signals may be more useful than upside sell signals for large-cap equities.

In practical terms:

Low z-score events may behave more like mean-reversion buy opportunities.
High z-score events may often reflect momentum rather than reliable short/sell opportunities.

This reflects an important market behavior: large-cap equities often have positive long-term drift, so upside extensions may continue instead of immediately reversing.

Project Structure
market-signal-scanner/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── src/
│   ├── api_client.py
│   ├── update_prices.py
│   └── config.py
│
├── notebooks/
│   └── market_signal_analysis.ipynb
│
├── data/
│   └── .gitkeep
│
└── assets/
    └── screenshots/
How the Pipeline Works
1. Pull Weekly Data
python src/update_prices.py

The update script pulls a rotating batch of symbols each day and stores weekly adjusted data in DuckDB.

2. Analyze in JupyterLab

The Jupyter notebook connects to the DuckDB database and performs:

Indicator calculation
Z-score scanning
Mean-reversion backtesting
Volatility analysis
Interactive visualization
3. Review Latest Signals

The latest-week scanner returns stocks with extreme readings across:

Adjusted close z-score
Adjusted high z-score
Adjusted low z-score
Example Backtest Output

The backtest summary includes:

signal_label
trades
avg_return
median_return
win_rate
total_return
best_trade
worst_trade
threshold

These metrics are used to compare signal quality across different thresholds and holding periods.

Interactive Visualizations

The notebook uses Plotly to create interactive charts, including:

Average strategy return by z-score threshold
Win rate by threshold
Bollinger-style bands
Adjusted close vs rolling mean
Latest signal scanner tables
Strategy performance comparisons
Scheduling

The update script can be scheduled with Windows Task Scheduler to run once per day.

The workflow is:

Task Scheduler → update_prices.py → DuckDB database → JupyterLab analysis

This keeps data ingestion separate from notebook-based analysis.

Important Limitations

This project is for research and education only.

Known limitations:

Uses a current symbol universe, which may introduce survivorship bias
Alpha Vantage free tier limits daily API requests
Weekly high/low signals are only fully known after the week closes
Backtests do not currently include transaction costs, slippage, taxes, or liquidity constraints
Signal results should not be interpreted as trading recommendations
Future Improvements

Potential next steps include:

Add SPY-relative strength metrics
Add sector ETF comparisons
Add 52-week trend filters
Add volatility-adjusted position sizing
Add transaction cost assumptions
Add train/test split to reduce overfitting
Add email alerts for extreme z-score readings
Build a dashboard view for the latest weekly scanner
Move project to a linux environment for cleaner automation
Resume Summary

Built an automated weekly stock data pipeline using Python, DuckDB, SQL, and Alpha Vantage to track 135+ equities and ETFs, calculate rolling z-score deviation signals, and backtest mean-reversion strategies across multiple thresholds and holding periods. Created interactive Plotly visualizations and scanner tables to evaluate current market opportunities using adjusted-close, adjusted-high, and adjusted-low metrics.
