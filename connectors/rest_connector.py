from pathlib import Path
import json
from datetime import datetime, timezone
from normalizer import normalize_market_ticks_to_events, normalize_orderflow_to_signals, seed_entities_for_symbols

def run_rest_connector(cfg: dict):
    source = cfg.get("source_name", "rest_source")
    output_dir = cfg.get("output_dir", f"live_output/{source}")
    symbols = cfg.get("symbols", ["SPY","QQQ","IPSA"])
    # Stub payload for v1: replace with real HTTP polling logic
    now = datetime.now(timezone.utc).isoformat()
    ticks = [{"symbol": s, "price": 100 + i * 3.5, "timestamp": now} for i, s in enumerate(symbols, start=1)]
    signals = [{"entity_id": s, "signal_type": "volatility_shift", "severity": round(0.25 + i*0.1, 2), "timestamp": now} for i, s in enumerate(symbols, start=1)]
    seed_entities_for_symbols(symbols, output_dir)
    n1 = normalize_market_ticks_to_events(source, ticks, output_dir)
    n2 = normalize_orderflow_to_signals(source, signals, output_dir)
    print(f"[rest] {source}: wrote {n1} events, {n2} signals → {output_dir}")
