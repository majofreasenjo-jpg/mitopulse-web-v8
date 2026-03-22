from __future__ import annotations
from backend.v79_core.core.helpers import clamp

class DefenseEngine:
    def compute(self, raw):
        guardian_activation = clamp(raw["defense_activation"])
        self_defense_mode = guardian_activation > 0.62
        quarantine_pressure = clamp(raw["propagation_pressure"] * 0.55 + raw["identity_drift"] * 0.45)
        return {
            "guardian_activation": round(guardian_activation, 4),
            "self_defense_mode": self_defense_mode,
            "quarantine_pressure": round(quarantine_pressure, 4),
        }
