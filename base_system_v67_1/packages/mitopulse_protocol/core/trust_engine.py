from mitopulse_protocol.models.objects import TrustProfile
from mitopulse_protocol.state_machines.trust import TrustStateMachine
class TrustEngine:
    def compute(self, entity_id: str, trust_score: float, trust_velocity: float, trust_volatility: float):
        sm = TrustStateMachine()
        if trust_score >= 0.10: sm.transition("NEUTRAL")
        if trust_score >= 0.45: sm.transition("TRUSTED")
        if trust_score >= 0.70: sm.transition("RELIABLE")
        if trust_score >= 0.90: sm.transition("CRITICAL_TRUST")
        if trust_score < 0.25 and sm.state in {"NEUTRAL","TRUSTED","RELIABLE","CRITICAL_TRUST"}:
            sm.state = "COMPROMISED"
        reserve = max(0.0, round(trust_score - trust_volatility + max(trust_velocity,0.0),3))
        return TrustProfile(entity_id, round(trust_score,3), round(trust_velocity,3), round(trust_volatility,3), reserve, sm.state)
