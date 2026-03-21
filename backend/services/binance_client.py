from __future__ import annotations
import requests

BINANCE_BASE = "https://api.binance.com"

def get_ticker(symbol: str = "BTCUSDT") -> dict:
    r = requests.get(f"{BINANCE_BASE}/api/v3/ticker/24hr", params={"symbol": symbol.upper()}, timeout=10)
    r.raise_for_status()
    j = r.json()
    return {
        "symbol": symbol.upper(),
        "last_price": float(j["lastPrice"]),
        "price_change_percent": float(j["priceChangePercent"]),
        "quote_volume": float(j["quoteVolume"]),
        "high_price": float(j["highPrice"]),
        "low_price": float(j["lowPrice"]),
        "open_price": float(j["openPrice"]),
        "count": int(j["count"]),
    }

def get_multi_tickers(symbols: list[str]) -> list[dict]:
    out = []
    for s in symbols:
        try:
            out.append(get_ticker(s))
        except Exception as e:
            out.append({"symbol": s, "error": str(e)})
    return out
