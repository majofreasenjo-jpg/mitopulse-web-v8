from __future__ import annotations
from backend.v79_core.engines.baseline import BaselineEngine
from backend.v79_core.engines.identity import IdentityEngine
from backend.v79_core.engines.behavior import BehaviorEngine
from backend.v79_core.engines.relational import RelationalEngine
from backend.v79_core.engines.propagation import PropagationEngine
from backend.v79_core.engines.physics import PhysicsEngine
from backend.v79_core.engines.biology import BiologyEngine
from backend.v79_core.engines.defense import DefenseEngine
from backend.v79_core.engines.quantum import QuantumEngine
from backend.v79_core.engines.risk import RiskEngine
from backend.v79_core.engines.probabilistic import ProbabilisticEngine
from backend.v79_core.engines.simulation import SimulationEngine
from backend.v79_core.engines.explainability import ExplainabilityEngine
from backend.v79_core.models import ExecutiveState, ProtocolSnapshot, GraphNode

class Orchestrator:
    def __init__(self):
        self.baseline = BaselineEngine()
        self.identity = IdentityEngine()
        self.behavior = BehaviorEngine()
        self.relational = RelationalEngine()
        self.propagation = PropagationEngine()
        self.physics = PhysicsEngine()
        self.biology = BiologyEngine()
        self.defense = DefenseEngine()
        self.quantum = QuantumEngine()
        self.risk = RiskEngine()
        self.prob = ProbabilisticEngine()
        self.sim = SimulationEngine()
        self.explain = ExplainabilityEngine()

    def _derive_state(self, scr, avs):
        if scr < 0.28 and avs > 0.72:
            return "coherent"
        elif scr < 0.45 and avs > 0.60:
            return "stressed"
        elif scr < 0.62 and avs > 0.50:
            return "compensating"
        elif scr < 0.78 and avs > 0.35:
            return "degraded-but-viable"
        elif scr < 0.90:
            return "near-fracture"
        return "reconstituting"

    def _top_drivers(self, merged):
        candidates = [
            ("identity coherence drift", 1 - merged["identity_coherence_score"]),
            ("behavioral predation / drift", merged["behavioral_predation_index"]),
            ("propagation pressure", merged["contagion_level"]),
            ("systemic strain accumulation", merged["ssi"]),
            ("loss of homeostatic compensation", merged["msi"]),
            ("fracture probability", merged["fpi"]),
        ]
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in candidates[:4]]

    def _actions(self, state):
        mapping = {
            "coherent": ["monitor"],
            "stressed": ["enhanced_monitoring"],
            "compensating": ["review_and_limit"],
            "degraded-but-viable": ["review_and_limit", "isolate"],
            "near-fracture": ["block_or_freeze", "isolate", "recover"],
            "reconstituting": ["recover", "enhanced_monitoring"],
        }
        return mapping.get(state, ["monitor"])

    def build_state(self, raw):
        merged = {}
        for part in [
            self.baseline.compute(raw),
            self.identity.compute(raw),
            self.behavior.compute(raw),
            self.relational.compute(raw),
            self.propagation.compute(raw),
            self.physics.compute(raw),
            self.biology.compute(raw),
            self.defense.compute(raw),
            self.quantum.compute(raw),
        ]:
            merged.update(part)

        merged.update(self.risk.compute(merged))
        merged.update(self.prob.compute(merged))

        state = self._derive_state(merged["scr"], merged["avs"])
        drivers = self._top_drivers(merged)
        explanation = self.explain.summarize(state, drivers)
        actions = self._actions(state)

        return ExecutiveState(
            tick=raw["tick"],
            state=state,
            nhi=merged["nhi"],
            tpi=merged["tpi"],
            scr=merged["scr"],
            aci=merged["aci"],
            avs=merged["avs"],
            metabolic_load=merged["metabolic_load"],
            homeostasis_stability=round(max(0.0, min(1.0, 1 - merged["msi"])), 4),
            reflex_activation_count=int(round(raw["defense_activation"] * 10)),
            behavioral_predation_index=merged["behavioral_predation_index"],
            cycle_recurrence_risk=merged["cycle_recurrence_risk"],
            fdi=merged["fdi"],
            ssi=merged["ssi"],
            cfi=merged["cfi"],
            fpi=merged["fpi"],
            sei=merged["sei"],
            msi=merged["msi"],
            pmi=merged["pmi"],
            aes=merged["aes"],
            collapse_probability=merged["collapse_probability"],
            time_to_criticality=merged["time_to_criticality"],
            confidence_low=merged["confidence_low"],
            confidence_high=merged["confidence_high"],
            top_drivers=drivers,
            actions=actions,
            explanation=explanation
        )

    def project_state(self, raw, horizon="24h"):
        steps = 12 if horizon == "24h" else 6
        projected_raw = self.sim.project(raw, steps=steps)
        projected_raw["tick"] = raw["tick"] + steps
        return self.build_state(projected_raw)

    def protocol_snapshot(self, state: ExecutiveState, identity_state="verified", crypto_state="transition-ready"):
        if state.state == "coherent":
            protocol_state = "normal"
        elif state.state in ("stressed", "compensating"):
            protocol_state = "heightened"
        elif state.state == "degraded-but-viable":
            protocol_state = "degraded"
        else:
            protocol_state = "self-defending"
        notes = [
            f"Actions: {', '.join(state.actions)}",
            f"Collapse probability: {state.collapse_probability}",
            f"Time to criticality: {state.time_to_criticality}h-eq"
        ]
        return ProtocolSnapshot(
            protocol_state=protocol_state,
            identity_state=identity_state,
            crypto_state=crypto_state,
            autopoietic_state=state.state,
            drivers=state.top_drivers,
            notes=notes
        )

    def graph_nodes(self, state: ExecutiveState):
        base = [
            ("ID-H1", "human", max(0.05, min(1.0, 1 - state.aci)), state.aci, "identity"),
            ("ID-A1", "agent", state.aes, state.aci, "identity"),
            ("REL-C1", "cluster", state.tpi, state.nhi, "relational"),
            ("PHY-S1", "strain", state.ssi, max(0.0, 1 - state.ssi), "physics"),
            ("BIO-H1", "homeostasis", state.msi, max(0.0, 1 - state.msi), "biology"),
            ("RISK-R1", "risk", state.scr, max(0.0, 1 - state.scr), "risk"),
        ]
        return [GraphNode(id=i, role=r, risk=round(k,4), coherence=round(c,4), zone=z) for i, r, k, c, z in base]
