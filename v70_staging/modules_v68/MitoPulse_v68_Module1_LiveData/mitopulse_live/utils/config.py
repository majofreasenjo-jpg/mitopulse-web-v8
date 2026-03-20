import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
COINGECKO_BASE_URL = os.getenv("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10"))
DEFAULT_SYMBOLS = [
    s.strip().upper()
    for s in os.getenv(
        "DEFAULT_SYMBOLS",
        "BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT,ADAUSDT,AVAXUSDT,DOGEUSDT,MATICUSDT,TONUSDT",
    ).split(",")
    if s.strip()
]
