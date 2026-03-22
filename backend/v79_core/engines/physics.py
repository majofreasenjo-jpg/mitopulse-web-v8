from __future__ import annotations
from backend.v79_core.core.helpers import clamp

class PhysicsEngine:
    def compute(self, raw):
        fdi = clamp(raw["propagation_pressure"] * 0.4 + raw["relational_density"] * 0.6)
        ssi = clamp(raw["structural_strain"])
        cfi = clamp(raw["structural_strain"] * 0.65 + raw["behavior_noise"] * 0.35)
        fpi = clamp(raw["structural_strain"] * 0.55 + raw["homeostasis_loss"] * 0.45)
        fei = clamp(raw["energy_flow"])
        nei = clamp(raw["mutation_pressure"] * 0.5 + raw["behavior_noise"] * 0.5)
        fsi = clamp(1 - (0.55 * raw["propagation_pressure"] + 0.45 * raw["structural_strain"]))
        ori = clamp(raw["propagation_pressure"] * 0.52 + raw["homeostasis_loss"] * 0.48)
        dti = clamp(raw["homeostasis_loss"] * 0.62 + raw["behavior_noise"] * 0.38)
        return {
            "fdi": round(fdi, 4),
            "ssi": round(ssi, 4),
            "cfi": round(cfi, 4),
            "fpi": round(fpi, 4),
            "fei": round(fei, 4),
            "nei": round(nei, 4),
            "fsi": round(fsi, 4),
            "ori": round(ori, 4),
            "dti": round(dti, 4),
        }
