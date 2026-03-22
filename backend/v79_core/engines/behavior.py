from __future__ import annotations
from backend.v79_core.core.helpers import clamp

class BehaviorEngine:
    def compute(self, raw):
        predation = clamp(raw["behavior_noise"] * 0.55 + raw["mutation_pressure"] * 0.45)
        continuity = clamp(1 - (raw["behavior_noise"] * 0.70 + raw["identity_drift"] * 0.30))
        cycle_risk = clamp(raw["propagation_pressure"] * 0.35 + raw["behavior_noise"] * 0.65)
        return {
            "behavioral_predation_index": round(predation, 4),
            "behavioral_continuity_score": round(continuity, 4),
            "cycle_recurrence_risk": round(cycle_risk, 4),
        }
