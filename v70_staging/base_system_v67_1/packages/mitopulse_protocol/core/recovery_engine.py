from mitopulse_protocol.models.objects import RecoveryProfile
from mitopulse_protocol.state_machines.recovery import RecoveryStateMachine
class RecoveryEngine:
    def recover(self, stability_score: float):
        sm = RecoveryStateMachine()
        if stability_score >= 0.20: sm.transition("CONTAINMENT")
        if stability_score >= 0.40: sm.transition("STABILIZATION")
        if stability_score >= 0.60: sm.transition("RECOVERY")
        if stability_score >= 0.80: sm.transition("REINTEGRATION")
        if stability_score >= 0.95: sm.transition("ADAPTATION")
        return RecoveryProfile(sm.state, round(stability_score,3), sm.state in {"REINTEGRATION","ADAPTATION"})
