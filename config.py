import os
from pathlib import Path

BASE_URL = "https://www.alphavantage.co/query"
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "market_data.duckdb"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)