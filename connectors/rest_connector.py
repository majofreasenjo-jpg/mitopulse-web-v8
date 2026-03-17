import requests
from datetime import datetime, timezone
from normalizer import (
    normalize_market_ticks_to_events,
    normalize_orderflow_to_signals,
    seed_entities_for_symbols
)

def fetch_yahoo_quote(symbol: str):
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
    r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    payload = r.json()
    result = payload.get("quoteResponse", {}).get("result", [])
    if not result:
        return None
    q = result[0]
    return {
        "symbol": symbol,
        "price": q.get("regularMarketPrice", 0) or 0,
        "change_pct": q.get("regularMarketChangePercent", 0) or 0,
        "volume": q.get("regularMarketVolume", 0) or 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def run_rest_connector(cfg: dict):
    source = cfg.get("source_name", "yahoo_live_market")
    output_dir = cfg.get("output_dir", f"live_output/{source}")
    symbols = cfg.get("symbols", ["AAPL", "MSFT", "TSLA", "SPY", "NVDA"])

    seed_entities_for_symbols(symbols, output_dir)

    ticks = []
    signals = []
    for s in symbols:
        try:
            quote = fetch_yahoo_quote(s)
        except Exception as e:
            print(f"[rest] {source}: error fetching {s}: {e}")
            continue
        if not quote:
            continue

        ticks.append({
            "symbol": quote["symbol"],
            "price": quote["price"],
            "timestamp": quote["timestamp"]
        })

        severity = min(1.0, abs(float(quote["change_pct"])) / 10.0)
        signal_type = "volatility_shift" if severity >= 0.35 else "market_movement"
        signals.append({
            "entity_id": quote["symbol"],
            "signal_type": signal_type,
            "severity": round(severity, 3),
            "timestamp": quote["timestamp"]
        })

    n1 = normalize_market_ticks_to_events(source, ticks, output_dir)
    n2 = normalize_orderflow_to_signals(source, signals, output_dir)
    print(f"[rest] {source}: wrote {n1} events, {n2} signals → {output_dir}")
