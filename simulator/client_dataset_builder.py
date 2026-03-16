from pathlib import Path
import pandas as pd
import random
from datetime import datetime, timedelta

R = random.Random(42)

SCENARIOS = {
    "bank": {"customers": 1000, "events": 3800, "devices": 1200, "signals": 100},
    "marketplace": {"customers": 1400, "events": 4500, "devices": 1500, "signals": 140},
    "telco": {"customers": 900, "events": 2600, "devices": 1100, "signals": 120},
}

def pick(seq):
    return seq[R.randrange(0, len(seq))]

def make_dataset(output_dir: str, client_type: str = "bank"):
    cfg = SCENARIOS[client_type]
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    customers, devices, events, signals = [], [], [], []

    customer_ids = [f"CUST_{i:05d}" for i in range(cfg["customers"])]
    externals = [f"EXT_{i:03d}" for i in range(20)]
    mules = [f"MULE_{i:03d}" for i in range(8)]
    bad = [f"BAD_{i:03d}" for i in range(12)]
    start = datetime(2026, 1, 1)

    for cid in customer_ids:
        customers.append({
            "customer_id": cid,
            "name_hash": f"nm_{abs(hash(cid)) % 10**9}",
            "phone_hash": f"ph_{abs(hash(cid+'_p')) % 10**10}",
            "email_hash": f"em_{abs(hash(cid+'_e')) % 10**10}",
            "segment": pick(["mass", "premium", "new", "young"]),
            "region": pick(["north", "center", "south"]),
            "created_at": (start + timedelta(days=R.randint(0, 365))).isoformat()
        })

    for i in range(cfg["devices"]):
        cid = pick(customer_ids)
        devices.append({
            "device_id": f"DEV_{i:05d}",
            "customer_id": cid,
            "device_hash": f"dh_{abs(hash(cid+str(i))) % 10**12}",
            "channel": pick(["mobile_app", "web", "call_center"]),
            "risk_hint": pick(["normal", "normal", "new_device", "new_channel"])
        })

    labels = ["normal"] * (cfg["events"] - 350) + ["mule_pattern"] * 170 + ["scam_ring"] * 110 + ["social_chain"] * 70
    R.shuffle(labels)
    for i, label in enumerate(labels):
        sender = pick(customer_ids if label != "scam_ring" else bad)
        if label == "mule_pattern":
            receiver = pick(mules); context = "urgent_transfer"; event_type = "transfer"
        elif label == "scam_ring":
            receiver = pick(customer_ids[250:700]); context = "fake_receipt"; event_type = pick(["marketplace_chat", "payment_release"])
        elif label == "social_chain":
            receiver = pick(mules + bad); context = "social_engineering"; event_type = "transfer"
        else:
            receiver = pick(customer_ids + externals); context = pick(["general", "family", "salary", "commerce"]); event_type = pick(["transfer", "p2p", "marketplace_payment", "message"])
        if sender == receiver:
            receiver = pick(externals)
        events.append({
            "event_id": f"EVT_{i:06d}",
            "source_id": sender,
            "target_id": receiver,
            "event_type": event_type,
            "context": context,
            "amount": R.randint(8, 2500),
            "label": label,
            "timestamp": (start + timedelta(minutes=i*3)).isoformat()
        })

    for i in range(cfg["signals"]):
        entity = pick(customer_ids + externals + mules + bad)
        signals.append({
            "signal_id": f"SIG_{i:05d}",
            "entity_id": entity,
            "signal_type": pick(["new_channel", "identity_shift", "unknown_relationship", "shared_signal_detected", "sim_swap_hint", "device_reset"]),
            "severity": round(R.uniform(0.25, 0.98), 3),
            "source": pick(["bank", "marketplace", "telco", "wallet"]),
            "timestamp": (start + timedelta(hours=i)).isoformat()
        })

    pd.DataFrame(customers).to_csv(out / "customers.csv", index=False)
    pd.DataFrame(devices).to_csv(out / "devices.csv", index=False)
    pd.DataFrame(events).to_csv(out / "events.csv", index=False)
    pd.DataFrame(signals).to_csv(out / "signals.csv", index=False)
