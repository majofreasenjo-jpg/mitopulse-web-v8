def compute_quorum(votes):
    if not votes:
        return 0.0, False
    approvals = sum(1 for v in votes if v["vote"] == "approve")
    score = approvals / len(votes)
    return round(score, 3), score >= 0.70
