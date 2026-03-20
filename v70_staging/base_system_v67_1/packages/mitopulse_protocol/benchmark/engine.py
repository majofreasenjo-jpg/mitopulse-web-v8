import statistics
from mitopulse_protocol.connectors.normalizer import normalize_event

def baseline_signal(ticker: dict) -> dict:
    change = float(ticker["price_change_percent"])
    triggered = change <= -2.0
    return {
        "system": "baseline_rule",
        "triggered": triggered,
        "severity": "alert" if triggered else "none",
        "reason": "price_change_percent <= -2.0"
    }

def ml_simple_signal(ticker: dict, klines: list) -> dict:
    closes = [k["close"] for k in klines]
    last_close = closes[-1]
    mean_close = statistics.mean(closes)
    stdev_close = statistics.pstdev(closes) or 1e-6
    z = (last_close - mean_close) / stdev_close
    triggered = abs(z) >= 1.5
    return {
        "system": "ml_zscore",
        "triggered": triggered,
        "zscore": round(z, 4),
        "severity": "alert" if triggered else "none",
        "reason": "abs(zscore) >= 1.5"
    }

def to_protocol_payload(ticker: dict, klines: list, symbol: str) -> dict:
    closes = [k["close"] for k in klines]
    volumes = [k["volume"] for k in klines]
    last_close = closes[-1]
    mean_close = statistics.mean(closes)
    stdev_close = statistics.pstdev(closes) or 1e-6
    z = (last_close - mean_close) / stdev_close
    vol_ratio = (volumes[-1] / (statistics.mean(volumes) or 1e-6))
    change = float(ticker["price_change_percent"])
    return normalize_event("binance_real", {
        "entity_id": symbol,
        "entity_type": "crypto_pair",
        "evidence_score": min(0.98, 0.42 + abs(change)/10),
        "trust_score": max(0.05, 0.95 - abs(change)/8),
        "trust_velocity": max(-0.12, min(0.12, z/10)),
        "trust_volatility": min(0.40, abs(z)/6),
        "load_dev": min(95.0, 25 + abs(change)*10 + max(0, (vol_ratio-1))*20),
        "entropy_dev": min(95.0, 15 + abs(z)*18),
        "coordination_signal": min(95.0, 10 + max(0, (vol_ratio-1))*38 + abs(change)*6),
        "trust_break": min(95.0, abs(change)*8 + abs(z)*12),
        "structural_distortion": min(95.0, abs(z)*10 + max(0, (vol_ratio-1))*30),
        "confidence": 0.84 if abs(z) < 1.5 else 0.92,
        "quorum_score": 0.78 if vol_ratio < 1.4 else 0.86,
        "recovery_stability_score": max(0.20, 0.90 - abs(change)/10)
    })

def detect_lead_time_placeholder(baseline: dict, ml: dict, protocol_result) -> dict:
    risk_state = getattr(protocol_result["risk"], "risk_state", "UNKNOWN")
    protocol_triggered = risk_state in {"PRESSURE", "INSTABILITY", "CRITICAL", "COLLAPSE"}
    lead_advantage = 0
    if protocol_triggered and not baseline["triggered"]:
        lead_advantage = 1
    if protocol_triggered and not ml["triggered"]:
        lead_advantage += 1
    return {
        "protocol_triggered": protocol_triggered,
        "lead_advantage_units": lead_advantage
    }
