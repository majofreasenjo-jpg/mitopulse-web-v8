from mitopulse_protocol.models.objects import EntityObject
from mitopulse_protocol.state_machines.identity import IdentityStateMachine
class IdentityEngine:
    def evaluate(self, entity_id: str, entity_type: str, evidence_score: float):
        sm = IdentityStateMachine()
        if evidence_score > 0.05: sm.transition("OBSERVED")
        if evidence_score > 0.20: sm.transition("CONTEXTUALIZED")
        if evidence_score > 0.40: sm.transition("TRUSTED")
        if evidence_score > 0.65: sm.transition("VERIFIED")
        if evidence_score > 0.85: sm.transition("ANCHORED")
        return EntityObject(entity_id, entity_type, sm.state, round(evidence_score,3), {"evidence_score": round(evidence_score,3)}, {"centrality_proxy": round(evidence_score*10,2)})
