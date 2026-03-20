from mitopulse_federation.engine.quorum import weighted_quorum


def test_weighted_quorum():
    votes = [
        {"trust_weight": 0.9, "decision": "approve"},
        {"trust_weight": 0.8, "decision": "approve"},
        {"trust_weight": 0.7, "decision": "approve"},
    ]
    out = weighted_quorum(votes, threshold=0.67)
    assert out["approved"] is True
    assert out["weighted_score"] > 0.9
