from statistics import mean, pstdev
from typing import Any, Dict, List


def normalize_market_snapshot(ticker: Dict[str, Any], klines: List[Dict[str, Any]]) -> Dict[str, Any]:
    closes = [k["close"] for k in klines]
    volumes = [k["volume"] for k in klines]

    last_close = closes[-1]
    mean_close = mean(closes)
    stdev_close = pstdev(closes) or 1e-6
    zscore = (last_close - mean_close) / stdev_close

    last_volume = volumes[-1]
    mean_volume = mean(volumes) or 1e-6
    volume_ratio = last_volume / mean_volume

    change = abs(float(ticker["price_change_percent"]))

    evidence_score = min(0.99, 0.35 + change / 12.0 + abs(zscore) / 8.0)
    trust_score = max(0.05, 0.97 - change / 10.0)
    trust_velocity = max(-0.20, min(0.20, zscore / 10.0))
    trust_volatility = min(0.50, abs(zscore) / 6.0)

    load_dev = min(99.0, 20.0 + change * 10.0 + max(0.0, volume_ratio - 1.0) * 20.0)
    entropy_dev = min(99.0, 10.0 + abs(zscore) * 18.0)
    coordination_signal = min(99.0, 8.0 + max(0.0, volume_ratio - 1.0) * 35.0 + change * 5.0)
    trust_break = min(99.0, change * 7.0 + abs(zscore) * 10.0)
    structural_distortion = min(99.0, abs(zscore) * 12.0 + max(0.0, volume_ratio - 1.0) * 28.0)

    confidence = 0.92 if abs(zscore) >= 1.5 else 0.84
    quorum_score = 0.87 if volume_ratio >= 1.4 else 0.78
    recovery_stability_score = max(0.20, 0.90 - change / 12.0)

    return {
        "source": ticker["source"],
        "entity_id": ticker["symbol"],
        "entity_type": "crypto_pair",
        "market_snapshot": {
            "last_price": ticker["last_price"],
            "price_change_percent": ticker["price_change_percent"],
            "volume_quote": ticker["volume_quote"],
            "zscore": round(zscore, 4),
            "volume_ratio": round(volume_ratio, 4),
        },
        "protocol_payload": {
            "entity_id": ticker["symbol"],
            "entity_type": "crypto_pair",
            "evidence_score": round(evidence_score, 4),
            "trust_score": round(trust_score, 4),
            "trust_velocity": round(trust_velocity, 4),
            "trust_volatility": round(trust_volatility, 4),
            "load_dev": round(load_dev, 4),
            "entropy_dev": round(entropy_dev, 4),
            "coordination_signal": round(coordination_signal, 4),
            "trust_break": round(trust_break, 4),
            "structural_distortion": round(structural_distortion, 4),
            "confidence": round(confidence, 4),
            "quorum_score": round(quorum_score, 4),
            "recovery_stability_score": round(recovery_stability_score, 4),
        },
    }
