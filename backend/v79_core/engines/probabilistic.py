from __future__ import annotations
from backend.v79_core.core.helpers import clamp

class ProbabilisticEngine:
    def compute(self, data):
        collapse_prob = clamp(0.52 * data["scr"] + 0.28 * data["fpi"] + 0.20 * data["sai"])
        time_to_criticality = round(max(1.0, 36 * (1 - collapse_prob)), 2)
        low = clamp(collapse_prob - 0.08)
        high = clamp(collapse_prob + 0.08)
        aci = clamp(0.40 * data["identity_coherence_score"] + 0.35 * data["sri"] + 0.25 * (1 - data["msi"]))
        avs = clamp(0.45 * data["nhi"] + 0.35 * aci + 0.20 * (1 - data["scr"]))
        return {
            "collapse_probability": round(collapse_prob, 4),
            "time_to_criticality": time_to_criticality,
            "confidence_low": round(low, 4),
            "confidence_high": round(high, 4),
            "aci": round(aci, 4),
            "avs": round(avs, 4),
        }
