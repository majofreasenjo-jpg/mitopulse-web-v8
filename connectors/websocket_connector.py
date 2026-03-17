from datetime import datetime, timezone
from normalizer import normalize_market_ticks_to_events, normalize_orderflow_to_signals, seed_entities_for_symbols

def run_websocket_connector(cfg: dict):
    source = cfg.get("source_name", "websocket_source")
    output_dir = cfg.get("output_dir", f"live_output/{source}")
    symbols = cfg.get("symbols", ["BTCUSD","ETHUSD"])
    # Stub payload for v1: replace with real WebSocket client
    now = datetime.now(timezone.utc).isoformat()
    seed_entities_for_symbols(symbols, output_dir)
    ticks = [{"symbol": s, "price": 25000 + i * 1250, "timestamp": now} for i, s in enumerate(symbols, start=1)]
    signals = [{"entity_id": s, "signal_type": "liquidity_shift", "severity": round(0.4 + i*0.08, 2), "timestamp": now} for i, s in enumerate(symbols, start=1)]
    n1 = normalize_market_ticks_to_events(source, ticks, output_dir)
    n2 = normalize_orderflow_to_signals(source, signals, output_dir)
    print(f"[ws] {source}: wrote {n1} events, {n2} signals → {output_dir}")
