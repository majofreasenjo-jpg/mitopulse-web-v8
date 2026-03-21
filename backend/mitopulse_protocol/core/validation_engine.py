from datetime import datetime
from mitopulse_protocol.models.objects import ValidationProfile
from mitopulse_protocol.storage.repository import add_vote
from mitopulse_protocol.validation.quorum import compute_quorum

class ValidationEngine:
    def simulate_votes(self, evaluation_id: int, confidence: float, anchors: list):
        votes = []
        for i, a in enumerate(anchors):
            weighted = confidence * float(a["trust_weight"])
            vote = "approve" if weighted >= 0.55 else "reject"
            votes.append({"vote_id": f"VOTE_{evaluation_id}_{i}", "anchor_id": a["anchor_id"], "confidence": round(weighted,3), "vote": vote, "ts": datetime.now().isoformat()})
            add_vote(evaluation_id, votes[-1]["vote_id"], a["anchor_id"], votes[-1]["confidence"], vote, votes[-1]["ts"])
        return votes

    def validate(self, evaluation_id: int, confidence: float, anchors: list, confidence_threshold: float = 0.75, quorum_threshold: float = 0.70, challenge_window_open: bool = True):
        votes = self.simulate_votes(evaluation_id, confidence, anchors)
        quorum_score, quorum_ok = compute_quorum(votes)
        notes = []
        validated = True
        if confidence < confidence_threshold:
            notes.append("confidence_below_threshold")
            validated = False
        if quorum_score < quorum_threshold or not quorum_ok:
            notes.append("quorum_below_threshold")
            validated = False
        if challenge_window_open:
            notes.append("challenge_window_open")
        return ValidationProfile(round(confidence,3), round(quorum_score,3), validated, False, challenge_window_open, notes)
