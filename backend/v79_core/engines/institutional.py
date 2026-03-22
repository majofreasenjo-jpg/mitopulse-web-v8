from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class ViabilityState:
    tick: int
    nhi: float
    tpi: float
    scr: float
    aci: float
    avs: float
    identity_drift: float
    behavior_drift: float
    propagation_pressure: float
    systemic_strain: float
    homeostasis_loss: float
    state: str
    top_drivers: List[str]


class ViabilityEngine:
    @staticmethod
    def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, v))

    def compute(self, tick: int, drivers: Dict[str, float]) -> ViabilityState:
        identity_drift = drivers["identity_drift"]
        behavior_drift = drivers["behavior_drift"]
        propagation_pressure = drivers["propagation_pressure"]
        systemic_strain = drivers["systemic_strain"]
        homeostasis_loss = drivers["homeostasis_loss"]

        nhi = self._clamp(1.0 - (0.28 * identity_drift + 0.22 * behavior_drift + 0.25 * systemic_strain + 0.25 * homeostasis_loss))
        tpi = self._clamp(0.20 * identity_drift + 0.20 * behavior_drift + 0.35 * propagation_pressure + 0.25 * systemic_strain)
        scr = self._clamp((0.45 * tpi) + (0.35 * (1.0 - nhi)) + (0.20 * homeostasis_loss))
        aci = self._clamp(1.0 - (0.30 * homeostasis_loss + 0.25 * systemic_strain + 0.20 * identity_drift + 0.25 * propagation_pressure))
        avs = self._clamp(0.45 * nhi + 0.35 * aci + 0.20 * (1.0 - scr))

        if scr < 0.28 and avs > 0.72:
            state = "coherent"
        elif scr < 0.45 and avs > 0.60:
            state = "stressed"
        elif scr < 0.62 and avs > 0.50:
            state = "compensating"
        elif scr < 0.78 and avs > 0.35:
            state = "degraded-but-viable"
        elif scr < 0.90:
            state = "near-fracture"
        else:
            state = "reconstituting"

        pairs = [
            ("identity coherence drift", identity_drift),
            ("behavioral predation / drift", behavior_drift),
            ("propagation pressure", propagation_pressure),
            ("systemic strain accumulation", systemic_strain),
            ("loss of homeostatic compensation", homeostasis_loss),
        ]
        pairs.sort(key=lambda x: x[1], reverse=True)
        top_drivers = [name for name, _ in pairs[:3]]

        return ViabilityState(
            tick=tick,
            nhi=round(nhi, 4),
            tpi=round(tpi, 4),
            scr=round(scr, 4),
            aci=round(aci, 4),
            avs=round(avs, 4),
            identity_drift=round(identity_drift, 4),
            behavior_drift=round(behavior_drift, 4),
            propagation_pressure=round(propagation_pressure, 4),
            systemic_strain=round(systemic_strain, 4),
            homeostasis_loss=round(homeostasis_loss, 4),
            state=state,
            top_drivers=top_drivers,
        )

    def as_dict(self, state: ViabilityState) -> Dict:
        return asdict(state)
