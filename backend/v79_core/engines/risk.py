from __future__ import annotations
from backend.v79_core.core.helpers import clamp

class RiskEngine:
    def compute(self, data):
        nhi = clamp(0.42 * data["sri"] + 0.33 * (1 - data["msi"]) + 0.25 * data["identity_coherence_score"])
        tpi = clamp(0.35 * data["contagion_level"] + 0.25 * data["behavioral_predation_index"] + 0.20 * data["mdi"] + 0.20 * data["aes"])
        scr = clamp(0.45 * tpi + 0.35 * (1 - nhi) + 0.20 * data["fpi"])
        return {
            "nhi": round(nhi, 4),
            "tpi": round(tpi, 4),
            "scr": round(scr, 4),
        }
