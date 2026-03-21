import random
from mitopulse_protocol.connectors.normalizer import normalize_event

def fetch_market_signal(symbol: str = "SPY") -> dict:
    pressure = random.randint(18, 92)
    return normalize_event("market_connector", {
        "symbol": symbol,
        "entity_type": "market_symbol",
        "evidence_score": min(0.95, 0.28 + pressure/130),
        "trust_score": max(0.08, 1 - pressure/125),
        "trust_velocity": random.uniform(-0.06, 0.04),
        "trust_volatility": random.uniform(0.04, 0.22),
        "load_dev": random.uniform(25, 85),
        "entropy_dev": random.uniform(12, 60),
        "coordination_signal": random.uniform(18, 85),
        "trust_break": random.uniform(6, 74),
        "structural_distortion": random.uniform(10, 68),
        "confidence": random.uniform(0.72, 0.94),
        "quorum_score": random.uniform(0.66, 0.89),
        "recovery_stability_score": random.uniform(0.36, 0.88)
    })
