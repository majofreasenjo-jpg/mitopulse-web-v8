from mitopulse_protocol.models.objects import RiskProfile
from mitopulse_protocol.state_machines.risk import RiskStateMachine
class RiskEngine:
    def assess(self, load_dev: float, entropy_dev: float, coordination_signal: float, trust_break: float, structural_distortion: float):
        nhi = max(0.0, min(100.0, 100 - (0.55*load_dev + 0.45*entropy_dev)))
        tpi = max(0.0, min(100.0, 0.50*load_dev + 0.80*coordination_signal + 0.70*trust_break))
        mdi = max(0.0, min(100.0, 1.15*structural_distortion + 0.55*coordination_signal))
        scr = max(0.0, min(100.0, 0.35*(100-nhi) + 0.35*tpi + 0.30*mdi))
        sm = RiskStateMachine()
        if scr >= 15: sm.transition("DEVIATION")
        if scr >= 35: sm.transition("PRESSURE")
        if scr >= 55: sm.transition("INSTABILITY")
        if scr >= 75: sm.transition("CRITICAL")
        if scr >= 92: sm.transition("COLLAPSE")
        return RiskProfile(round(nhi,2), round(tpi,2), round(scr,2), round(mdi,2), sm.state)
