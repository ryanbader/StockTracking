from __future__ import annotations

import requests
import json
import time
from pathlib import Path

from config import API_KEY, BASE_URL

def fetch_weekly_prices(symbol: str) -> Path:
    symbol = symbol.upper()

    params = {
        "function": "TIME_SERIES_WEEKLY_ADJUSTED",
        "symbol": symbol,
        "apikey": API_KEY,
    }

    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    print(f"{symbol} response keys: {list(payload.keys())}")

    if "Error Message" in payload:
        raise ValueError(f"{symbol}: {payload['Error Message']}")

    if "Note" in payload:
        raise ValueError(f"{symbol}: rate limit hit - {payload['Note']}")

    if "Information" in payload:
        raise ValueError(f"{symbol}: {payload['Information']}")

    if "Weekly Adjusted Time Series" not in payload:
        raise ValueError(
            f"{symbol}: unexpected response shape. Keys returned: {list(payload.keys())}"
        )

    time_series = payload["Weekly Adjusted Time Series"]
    
    out_dir = Path("data/raw")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"{symbol.lower()}_temp.json"
    out_path.write_text(json.dumps(time_series, indent=2), encoding="utf-8")

    time.sleep(15)

    return out_path