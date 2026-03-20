import random
from mitopulse_protocol.connectors.normalizer import normalize_event

def fetch_banking_signal(entity_id: str = "txn_high_value") -> dict:
    anomaly = random.randint(12, 97)
    return normalize_event("banking_connector", {
        "entity_id": entity_id,
        "entity_type": "banking_transaction",
        "evidence_score": min(0.97, 0.30 + anomaly/135),
        "trust_score": max(0.03, 1 - anomaly/115),
        "trust_velocity": random.uniform(-0.09, 0.03),
        "trust_volatility": random.uniform(0.05, 0.26),
        "load_dev": random.uniform(30, 90),
        "entropy_dev": random.uniform(12, 64),
        "coordination_signal": random.uniform(12, 90),
        "trust_break": random.uniform(10, 80),
        "structural_distortion": random.uniform(12, 78),
        "confidence": random.uniform(0.76, 0.97),
        "quorum_score": random.uniform(0.69, 0.92),
        "recovery_stability_score": random.uniform(0.30, 0.80)
    })
