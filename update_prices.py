from __future__ import annotations

from datetime import date
from pathlib import Path
import json
import time

import duckdb
import pandas as pd

from api_client import fetch_weekly_prices
from config import DB_PATH


SYMBOLS = [
    "NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "AVGO", "TSLA", "META", "WMT",
    "BRK.B", "LLY", "MU", "JPM", "AMD", "XOM", "V", "ORCL", "INTC", "JNJ",
    "CSCO", "COST", "MA", "CAT", "CVX", "ABBV", "NFLX", "UNH", "LRCX", "BAC",
    "KO", "AMAT", "PG", "PLTR", "MS", "HD", "PM", "GE", "GEV", "GS",
    "TXN", "MRK", "KLAC", "LIN", "RTX", "WFC", "AXP", "QCOM", "C", "SNDK",
    "IBM", "ADI", "PEP", "TMUS", "PANW", "MCD", "NEE", "VZ", "ANET", "DIS",
    "STX", "AMGN", "BA", "APP", "BLK", "T", "WDC", "GLW", "TJX", "TMO",
    "GILD", "UNP", "SCHW", "DELL", "ETN", "APH", "UBER", "DE", "CRWD", "WELL",
    "ISRG", "COP", "ABT", "PFE", "BX", "VRT", "CRM", "HON", "PLD", "CB",
    "CVS", "LOW", "MO", "SBUX", "BKNG", "SPGI", "LMT", "SYK", "PGR", "COF",
    "NEM", "BMY", "PWR", "DHR", "VRTX", "PH", "INTU", "CME", "EQIX", "SO",
    "HWM", "ACN", "TT", "ADBE", "NOW", "MDT", "CEG", "SNPS", "CMI", "CDNS",
    "WMB", "DUK", "HCA", "MAR", "BK", "MCK", "FCX", "GD", "FTNT", "FDX",
    "CMCSA", "WM", "JCI", "ICE", "KKR", "SPY", "VIX", "XLK", "CLSK", "RGTI",
]

BATCH_SIZE = 20
REQUEST_SLEEP_SECONDS = 15
ROTATION_START_DATE = date(2026, 5, 16)

def get_today_symbols(symbols: list[str], batch_size: int = 20) -> list[str]:
    unique_symbols = list(dict.fromkeys([s.upper() for s in symbols]))

    days_since_start = (date.today() - ROTATION_START_DATE).days

    num_batches = (len(unique_symbols) + batch_size - 1) // batch_size
    batch_index = days_since_start % num_batches

    start = batch_index * batch_size
    end = start + batch_size

    return unique_symbols[start:end]


def ensure_tables(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("""
        CREATE TABLE IF NOT EXISTS stock_data (
            symbol VARCHAR,
            week_date DATE,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            adjusted_close DOUBLE,
            volume UBIGINT,
            dividend_amount DOUBLE,
            PRIMARY KEY(symbol, week_date)
        )
    """)


def build_weekly_dataframe(symbol: str, json_path: Path) -> pd.DataFrame:
    raw = json.loads(json_path.read_text(encoding="utf-8"))

    rows = [
        {
            "symbol": symbol.upper(),
            "week_date": week_date,
            "open": values["1. open"],
            "high": values["2. high"],
            "low": values["3. low"],
            "close": values["4. close"],
            "adjusted_close": values["5. adjusted close"],
            "volume": values["6. volume"],
            "dividend_amount": values["7. dividend amount"],
        }
        for week_date, values in raw.items()
    ]

    df = pd.DataFrame(rows)

    if df.empty:
        raise ValueError(f"{symbol}: no weekly rows found in {json_path}")

    df["symbol"] = df["symbol"].astype("string")
    df["week_date"] = pd.to_datetime(df["week_date"])

    float_cols = [
        "open",
        "high",
        "low",
        "close",
        "adjusted_close",
        "dividend_amount",
    ]

    for col in float_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["volume"] = pd.to_numeric(df["volume"], errors="coerce").astype("UInt64")

    return df


def upsert_stock_data(
    con: duckdb.DuckDBPyConnection,
    incoming_df: pd.DataFrame,
) -> None:
    con.register("incoming_stock_data", incoming_df)

    con.execute("""
        MERGE INTO stock_data AS target
        USING (
            SELECT
                symbol::VARCHAR AS symbol,
                week_date::DATE AS week_date,
                open::DOUBLE AS open,
                high::DOUBLE AS high,
                low::DOUBLE AS low,
                close::DOUBLE AS close,
                adjusted_close::DOUBLE AS adjusted_close,
                volume::UBIGINT AS volume,
                dividend_amount::DOUBLE AS dividend_amount
            FROM incoming_stock_data
        ) AS src
        ON target.symbol = src.symbol
           AND target.week_date = src.week_date

        WHEN MATCHED THEN UPDATE SET
            open = src.open,
            high = src.high,
            low = src.low,
            close = src.close,
            adjusted_close = src.adjusted_close,
            volume = src.volume,
            dividend_amount = src.dividend_amount

        WHEN NOT MATCHED THEN INSERT (
            symbol,
            week_date,
            open,
            high,
            low,
            close,
            adjusted_close,
            volume,
            dividend_amount
        ) VALUES (
            src.symbol,
            src.week_date,
            src.open,
            src.high,
            src.low,
            src.close,
            src.adjusted_close,
            src.volume,
            src.dividend_amount
        )
    """)

    con.unregister("incoming_stock_data")


def load_symbol(symbol: str) -> None:
    symbol = symbol.upper()

    json_path = fetch_weekly_prices(symbol)
    incoming_df = build_weekly_dataframe(symbol, json_path)

    with duckdb.connect(str(DB_PATH)) as con:
        ensure_tables(con)
        upsert_stock_data(con, incoming_df)

        final_count = con.execute("""
            SELECT COUNT(*) AS rows
            FROM stock_data
            WHERE symbol = ?
        """, [symbol]).fetchone()[0]

    print(
        f"Loaded {symbol}: "
        f"{len(incoming_df)} incoming rows, "
        f"{final_count} rows in stock_data"
    )


def run_daily_batch() -> None:
    symbols_today = get_today_symbols(SYMBOLS, batch_size=BATCH_SIZE)

    print(f"Today: {date.today()}")
    print(f"Updating {len(symbols_today)} symbols:")
    print(symbols_today)

    for symbol in symbols_today:
        try:
            load_symbol(symbol)
        except Exception as e:
            print(f"Failed {symbol}: {e}")

        time.sleep(REQUEST_SLEEP_SECONDS)


if __name__ == "__main__":
    run_daily_batch()

