from pathlib import Path
import random
from datetime import datetime, timedelta
import pandas as pd

def generate_dataset(folder, industry, size):
    cfg_map = {
        "small": {"customers": 800, "devices": 950, "events": 3200, "signals": 90},
        "medium": {"customers": 5000, "devices": 6200, "events": 22000, "signals": 450},
        "large": {"customers": 20000, "devices": 25000, "events": 100000, "signals": 1800},
    }
    cfg = cfg_map[size]
    rnd = random.Random(hash(industry + size) & 0xffffffff)
    out = Path(folder)
    out.mkdir(parents=True, exist_ok=True)

    if industry == "bank":
        normal_contexts = ["salary", "bill_payment", "family", "payroll", "commerce"]
        event_types = ["transfer", "p2p", "payment"]
    elif industry == "marketplace":
        normal_contexts = ["listing_purchase", "seller_payout", "marketplace_chat", "delivery_confirmed", "commerce"]
        event_types = ["marketplace_payment", "message", "payment_release"]
    else:
        normal_contexts = ["topup", "bill_payment", "new_channel", "service_usage", "device_change"]
        event_types = ["message", "service_payment", "device_event"]

    customer_ids = [f"CUST_{i:06d}" for i in range(cfg["customers"])]
    externals = [f"EXT_{i:04d}" for i in range(max(30, cfg["customers"]//80))]
    mules = [f"MULE_{i:04d}" for i in range(max(8, cfg["customers"]//300))]
    bad = [f"BAD_{i:04d}" for i in range(max(10, cfg["customers"]//250))]
    start = datetime(2026, 1, 1)

    customers = [{
        "customer_id": cid,
        "name_hash": f"nm_{abs(hash(cid)) % 10**9}",
        "phone_hash": f"ph_{abs(hash(cid+'_p')) % 10**10}",
        "email_hash": f"em_{abs(hash(cid+'_e')) % 10**10}",
        "segment": rnd.choice(["mass", "premium", "new", "young", "business"]),
        "region": rnd.choice(["north", "center", "south"]),
        "industry": industry,
        "client_size": size,
        "created_at": (start + timedelta(days=rnd.randint(0, 365))).isoformat()
    } for cid in customer_ids]
    pd.DataFrame(customers).to_csv(out / "customers.csv", index=False)

    devices = []
    for i in range(cfg["devices"]):
        cid = rnd.choice(customer_ids)
        devices.append({
            "device_id": f"DEV_{i:06d}",
            "customer_id": cid,
            "device_hash": f"dh_{abs(hash(cid+str(i))) % 10**12}",
            "channel": rnd.choice(["mobile_app", "web", "call_center", "api"]),
            "risk_hint": rnd.choice(["normal", "normal", "new_device", "new_channel", "device_reset"])
        })
    pd.DataFrame(devices).to_csv(out / "devices.csv", index=False)

    abnormal_total = int(cfg["events"] * (0.09 if size == "small" else 0.07 if size == "medium" else 0.05))
    mule_count = int(abnormal_total * 0.45)
    scam_count = int(abnormal_total * 0.32)
    social_count = abnormal_total - mule_count - scam_count
    labels = (["normal"] * (cfg["events"] - abnormal_total) +
              ["mule_pattern"] * mule_count +
              ["scam_ring"] * scam_count +
              ["social_chain"] * social_count)
    rnd.shuffle(labels)

    events = []
    for i, label in enumerate(labels):
        sender = rnd.choice(customer_ids if label != "scam_ring" else bad)
        if label == "mule_pattern":
            receiver = rnd.choice(mules)
            context = "urgent_transfer" if industry != "marketplace" else "seller_payout"
            event_type = "transfer" if industry != "marketplace" else "payment_release"
        elif label == "scam_ring":
            receiver = rnd.choice(customer_ids[max(1,len(customer_ids)//5):max(2,len(customer_ids)//2)])
            context = "fake_receipt" if industry != "telco" else "identity_shift"
            event_type = "marketplace_chat" if industry == "marketplace" else "message"
        elif label == "social_chain":
            receiver = rnd.choice(mules + bad)
            context = "social_engineering" if industry != "telco" else "sim_swap"
            event_type = "transfer" if industry != "telco" else "device_event"
        else:
            receiver = rnd.choice(customer_ids + externals)
            context = rnd.choice(normal_contexts)
            event_type = rnd.choice(event_types)
        if sender == receiver:
            receiver = rnd.choice(externals)
        amount_base = 2500 if industry == "bank" else 1800 if industry == "marketplace" else 900
        amount = rnd.randint(8, amount_base)
        if label != "normal":
            amount = int(amount * (1.2 if size == "small" else 1.1 if size == "medium" else 1.05))
        events.append({
            "event_id": f"EVT_{i:07d}",
            "source_id": sender,
            "target_id": receiver,
            "event_type": event_type,
            "context": context,
            "amount": amount,
            "label": label,
            "timestamp": (start + timedelta(minutes=i)).isoformat()
        })
    pd.DataFrame(events).to_csv(out / "events.csv", index=False)

    signals = []
    targets = customer_ids + externals + mules + bad
    signal_types = ["new_channel", "identity_shift", "unknown_relationship", "shared_signal_detected", "sim_swap_hint", "device_reset"]
    for i in range(cfg["signals"]):
        signals.append({
            "signal_id": f"SIG_{i:06d}",
            "entity_id": rnd.choice(targets),
            "signal_type": rnd.choice(signal_types),
            "severity": round(rnd.uniform(0.25, 0.98), 3),
            "source": rnd.choice(["bank", "marketplace", "telco", "wallet"]),
            "timestamp": (start + timedelta(hours=i)).isoformat()
        })
    pd.DataFrame(signals).to_csv(out / "signals.csv", index=False)
