from pathlib import Path
import csv
from collections import defaultdict

CANONICAL_FILES = ["customers.csv", "devices.csv", "events.csv", "signals.csv"]

def ensure_output_dir(base_path: str):
    p = Path(base_path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def append_rows(csv_path: Path, fieldnames, rows):
    write_header = not csv_path.exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)

def normalize_market_ticks_to_events(source_name: str, ticks: list, output_dir: str):
    out = ensure_output_dir(output_dir)
    rows = []
    for i, t in enumerate(ticks, start=1):
        symbol = t.get("symbol", "UNKNOWN")
        rows.append({
            "event_id": f"{source_name}_tick_{i}",
            "source_id": symbol,
            "target_id": symbol,
            "event_type": "market_tick",
            "context": "live_market",
            "amount": t.get("price", 0),
            "label": "normal",
            "timestamp": t.get("timestamp", "")
        })
    append_rows(out / "events.csv",
                ["event_id","source_id","target_id","event_type","context","amount","label","timestamp"],
                rows)
    return len(rows)

def normalize_orderflow_to_signals(source_name: str, items: list, output_dir: str):
    out = ensure_output_dir(output_dir)
    rows = []
    for i, s in enumerate(items, start=1):
        rows.append({
            "signal_id": f"{source_name}_sig_{i}",
            "entity_id": s.get("entity_id", s.get("symbol", "UNKNOWN")),
            "signal_type": s.get("signal_type", "market_shift"),
            "severity": s.get("severity", 0.5),
            "source": source_name,
            "timestamp": s.get("timestamp", "")
        })
    append_rows(out / "signals.csv",
                ["signal_id","entity_id","signal_type","severity","source","timestamp"],
                rows)
    return len(rows)

def seed_entities_for_symbols(symbols: list, output_dir: str):
    out = ensure_output_dir(output_dir)
    customers = []
    devices = []
    for sym in symbols:
        customers.append({
            "customer_id": sym,
            "name_hash": f"sym_{sym.lower()}",
            "phone_hash": f"ph_{abs(hash(sym))%10_000_000_000:010d}",
            "email_hash": f"em_{abs(hash('e'+sym))%10_000_000_000:010d}",
            "segment": "market_symbol",
            "region": "GLOBAL",
            "industry": "market_data",
            "client_size": "live",
            "created_at": "2026-01-01T00:00:00"
        })
        devices.append({
            "device_id": f"DEV_{sym}",
            "customer_id": sym,
            "device_hash": f"dh_{abs(hash('d'+sym))%1_000_000_000_000}",
            "channel": "live_connector",
            "risk_hint": "normal"
        })
    append_rows(out / "customers.csv",
                ["customer_id","name_hash","phone_hash","email_hash","segment","region","industry","client_size","created_at"],
                customers)
    append_rows(out / "devices.csv",
                ["device_id","customer_id","device_hash","channel","risk_hint"],
                devices)
