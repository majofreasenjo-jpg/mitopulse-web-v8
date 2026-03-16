from pathlib import Path
import pandas as pd

REQUIRED = {
    "customers.csv": ["customer_id"],
    "devices.csv": ["device_id", "customer_id"],
    "events.csv": ["event_id", "source_id", "target_id", "event_type", "context", "amount"],
    "signals.csv": ["signal_id", "entity_id", "signal_type", "severity"],
}

def load_client_folder(folder: str):
    d = Path(folder)
    loaded = {}
    for fname, cols in REQUIRED.items():
        f = d / fname
        if not f.exists():
            raise ValueError(f"Missing required file: {fname}")
        df = pd.read_csv(f)
        missing = [c for c in cols if c not in df.columns]
        if missing:
            raise ValueError(f"{fname} missing columns: {missing}")
        loaded[fname] = df
    return loaded["customers.csv"], loaded["devices.csv"], loaded["events.csv"], loaded["signals.csv"]

def dataset_profile(customers, devices, events, signals):
    return {
        "customers": len(customers),
        "devices": len(devices),
        "events": len(events),
        "signals": len(signals),
        "event_types": events["event_type"].value_counts().to_dict(),
        "contexts": events["context"].value_counts().head(10).to_dict()
    }
