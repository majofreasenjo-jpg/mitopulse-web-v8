import random
from mitopulse_protocol.connectors.normalizer import normalize_event

def fetch_crypto_signal(symbol: str = "BTCUSDT") -> dict:
    risk = random.randint(20, 96)
    return normalize_event("crypto_connector", {
        "symbol": symbol,
        "entity_type": "crypto_pair",
        "evidence_score": min(0.98, 0.35 + risk/140),
        "trust_score": max(0.05, 1 - risk/120),
        "trust_velocity": random.uniform(-0.08, 0.05),
        "trust_volatility": random.uniform(0.05, 0.24),
        "load_dev": random.uniform(35, 82),
        "entropy_dev": random.uniform(15, 58),
        "coordination_signal": random.uniform(20, 88),
        "trust_break": random.uniform(8, 72),
        "structural_distortion": random.uniform(12, 70),
        "confidence": random.uniform(0.74, 0.95),
        "quorum_score": random.uniform(0.68, 0.90),
        "recovery_stability_score": random.uniform(0.35, 0.84)
    })
