import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10"))
LOOKBACK_LIMIT = int(os.getenv("LOOKBACK_LIMIT", "180"))
MAX_LAG = int(os.getenv("MAX_LAG", "5"))
CORRELATION_THRESHOLD = float(os.getenv("CORRELATION_THRESHOLD", "0.25"))
DEFAULT_SYMBOLS = [
    s.strip().upper()
    for s in os.getenv(
        "DEFAULT_SYMBOLS",
        "BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT,ADAUSDT,AVAXUSDT,DOGEUSDT,MATICUSDT,TONUSDT"
    ).split(",")
    if s.strip()
]
