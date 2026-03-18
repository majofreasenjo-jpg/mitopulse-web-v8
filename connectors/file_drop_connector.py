from pathlib import Path
import csv
from normalizer import append_rows, ensure_output_dir

def run_file_drop_connector(cfg: dict):
    source = cfg.get("source_name", "file_drop_source")
    input_dir = Path(cfg.get("input_dir", "connectors/inbox"))
    output_dir = ensure_output_dir(cfg.get("output_dir", f"live_output/{source}"))
    input_dir.mkdir(parents=True, exist_ok=True)
    files = list(input_dir.glob("*.csv"))
    if not files:
        print(f"[file_drop] {source}: no files found in {input_dir}")
        return
    for fp in files:
        with open(fp, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        name = fp.name.lower()
        if "event" in name:
            append_rows(output_dir / "events.csv",
                        ["event_id","source_id","target_id","event_type","context","amount","label","timestamp"],
                        rows)
        elif "signal" in name:
            append_rows(output_dir / "signals.csv",
                        ["signal_id","entity_id","signal_type","severity","source","timestamp"],
                        rows)
        elif "customer" in name:
            append_rows(output_dir / "customers.csv",
                        ["customer_id","name_hash","phone_hash","email_hash","segment","region","industry","client_size","created_at"],
                        rows)
        elif "device" in name:
            append_rows(output_dir / "devices.csv",
                        ["device_id","customer_id","device_hash","channel","risk_hint"],
                        rows)
        print(f"[file_drop] {source}: imported {fp.name} → {output_dir}")
