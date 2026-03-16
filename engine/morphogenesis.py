from collections import Counter

def morphogenetic_growth_signature(events_df):
    labels = Counter(events_df["label"].tolist())
    total = max(len(events_df), 1)
    abnormal_ratio = (labels.get("mule_pattern", 0) + labels.get("scam_ring", 0) + labels.get("social_chain", 0)) / total
    bridge_proxy = len(events_df[events_df["target_id"].astype(str).str.startswith(("MULE_", "BAD_"))])
    signature = min(1.0, abnormal_ratio * 1.8 + bridge_proxy / max(total, 1))
    return {"abnormal_ratio": round(abnormal_ratio, 3), "bridge_proxy": int(bridge_proxy), "morphogenetic_signature": round(signature, 3)}
