from __future__ import annotations
from backend.v79_core.core.helpers import clamp

class RelationalEngine:
    def compute(self, raw):
        gravity = clamp(raw["relational_density"])
        shadow = clamp(raw["relational_density"] * 0.58 + raw["behavior_noise"] * 0.42)
        mdi = clamp(raw["relational_density"] * 0.55 + raw["structural_strain"] * 0.45)
        fgi = clamp(raw["propagation_pressure"] * 0.6 + raw["relational_density"] * 0.4)
        sri = clamp(1 - raw["structural_strain"] * 0.75)
        kni = clamp(raw["propagation_pressure"] * 0.42 + raw["identity_drift"] * 0.58)
        return {
            "relational_gravity": round(gravity, 4),
            "shadow_coordination": round(shadow, 4),
            "mdi": round(mdi, 4),
            "fgi": round(fgi, 4),
            "sri": round(sri, 4),
            "kni": round(kni, 4),
        }
