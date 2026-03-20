from typing import Dict, List


def weighted_quorum(votes: List[Dict], threshold: float = 0.67) -> Dict:
    if not votes:
        return {
            "approved": False,
            "threshold": threshold,
            "weighted_score": 0.0,
            "support_ratio": 0.0,
            "vote_count": 0,
        }

    total_weight = sum(float(v.get("trust_weight", 0.0)) for v in votes)
    support_weight = sum(
        float(v.get("trust_weight", 0.0))
        for v in votes
        if v.get("decision") in {"approve", "monitor", "restrict", "block"}
    )

    weighted_score = support_weight / total_weight if total_weight else 0.0
    support_ratio = len([v for v in votes if v.get("decision") in {"approve", "monitor", "restrict", "block"}]) / len(votes)

    return {
        "approved": weighted_score >= threshold,
        "threshold": threshold,
        "weighted_score": round(weighted_score, 4),
        "support_ratio": round(support_ratio, 4),
        "vote_count": len(votes),
    }
