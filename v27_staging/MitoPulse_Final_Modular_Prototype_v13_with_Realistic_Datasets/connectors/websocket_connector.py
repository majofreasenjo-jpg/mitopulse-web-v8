import json
import time
from datetime import datetime, timezone
import websocket
from normalizer import (
    normalize_market_ticks_to_events,
    normalize_orderflow_to_signals,
    seed_entities_for_symbols
)

BINANCE_STREAM = "wss://stream.binance.com:9443/ws"

def run_websocket_connector(cfg: dict):
    source = cfg.get("source_name", "binance_live_crypto")
    output_dir = cfg.get("output_dir", f"live_output/{source}")
    symbols = cfg.get("symbols", ["btcusdt", "ethusdt", "solusdt"])
    duration_seconds = int(cfg.get("duration_seconds", 15))

    pretty_symbols = [s.upper() for s in symbols]
    seed_entities_for_symbols(pretty_symbols, output_dir)

    ticks = []
    signals = []
    end_time = time.time() + duration_seconds

    def on_message(ws, message):
        nonlocal ticks, signals
        try:
            data = json.loads(message)
            symbol = data.get("s", "UNKNOWN")
            price = float(data.get("p", 0) or 0)
            qty = float(data.get("q", 0) or 0)
            ts = datetime.now(timezone.utc).isoformat()
            ticks.append({
                "symbol": symbol,
                "price": price,
                "timestamp": ts
            })
            severity = min(1.0, qty / 10.0)
            signals.append({
                "entity_id": symbol,
                "signal_type": "liquidity_shift",
                "severity": round(severity, 3),
                "timestamp": ts
            })
        except Exception as e:
            print(f"[ws] {source}: parse error: {e}")

        if time.time() >= end_time:
            ws.close()

    def on_error(ws, error):
        print(f"[ws] {source}: error: {error}")

    def on_open(ws):
        params = [f"{s.lower()}@trade" for s in symbols]
        payload = {"method": "SUBSCRIBE", "params": params, "id": 1}
        ws.send(json.dumps(payload))

    ws = websocket.WebSocketApp(
        BINANCE_STREAM,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
    )
    ws.run_forever()

    # keep only last event per symbol if feed is too chatty
    if ticks:
        n1 = normalize_market_ticks_to_events(source, ticks[-200:], output_dir)
        n2 = normalize_orderflow_to_signals(source, signals[-200:], output_dir)
    else:
        n1 = n2 = 0
    print(f"[ws] {source}: wrote {n1} events, {n2} signals → {output_dir}")
