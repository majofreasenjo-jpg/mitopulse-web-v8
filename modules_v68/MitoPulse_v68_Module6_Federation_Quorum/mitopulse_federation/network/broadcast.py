from typing import Dict, List


def build_demo_votes(entity_id: str, signal: float, validators: List[Dict]) -> List[Dict]:
    votes = []
    for v in validators:
        if signal >= 0.85:
            decision = "block"
        elif signal >= 0.65:
            decision = "restrict"
        elif signal >= 0.45:
            decision = "monitor"
        else:
            decision = "approve"

        votes.append({
            "entity_id": entity_id,
            "node_id": v["node_id"],
            "label": v["label"],
            "trust_weight": v["trust_weight"],
            "decision": decision,
            "confidence": round(min(0.99, 0.55 + signal * 0.4), 4),
            "reason": f"federated validation based on signal={signal}"
        })
    return votes
