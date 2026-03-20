
def quorum(votes):
    if not votes:
        return {"approved": False, "threshold": 0.67, "weighted_score": 0.0, "support_ratio": 0.0, "vote_count": 0}
    avg = sum(votes) / len(votes)
    return {
        "approved": avg >= 0.67,
        "threshold": 0.67,
        "weighted_score": round(avg, 4),
        "support_ratio": 1.0,
        "vote_count": len(votes)
    }
