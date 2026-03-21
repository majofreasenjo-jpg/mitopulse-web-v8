import requests
from datetime import datetime

BINANCE_24H = "https://api.binance.com/api/v3/ticker/24hr"
BINANCE_KLINES = "https://api.binance.com/api/v3/klines"

def get_24h_ticker(symbol: str = "BTCUSDT") -> dict:
    r = requests.get(BINANCE_24H, params={"symbol": symbol}, timeout=10)
    r.raise_for_status()
    j = r.json()
    return {
        "symbol": symbol,
        "last_price": float(j["lastPrice"]),
        "price_change_percent": float(j["priceChangePercent"]),
        "quote_volume": float(j["quoteVolume"]),
        "volume": float(j["volume"]),
        "high_price": float(j["highPrice"]),
        "low_price": float(j["lowPrice"]),
        "event_ts": datetime.utcnow().isoformat()
    }

def get_recent_klines(symbol: str = "BTCUSDT", interval: str = "1m", limit: int = 60) -> list:
    r = requests.get(BINANCE_KLINES, params={"symbol": symbol, "interval": interval, "limit": limit}, timeout=10)
    r.raise_for_status()
    data = r.json()
    out = []
    for row in data:
        out.append({
            "open_time": int(row[0]),
            "open": float(row[1]),
            "high": float(row[2]),
            "low": float(row[3]),
            "close": float(row[4]),
            "volume": float(row[5])
        })
    return out
