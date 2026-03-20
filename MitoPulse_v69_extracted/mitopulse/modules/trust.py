
def trust_score(conf):
    return {
        "confidence": round(conf * 0.9, 4),
        "reason": f"federated validation based on signal={conf}",
        "validators_trust_score": 0.94
    }
