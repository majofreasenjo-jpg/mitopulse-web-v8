import pandas as pd
from core.fraud_detection_engine import FraudDetectionEngine
from core.relational_dark_matter import RelationalDarkMatter
from core.relational_wave_engine import RelationalWaveEngine
from core.fraud_evolution_engine import FraudEvolutionEngine
from core.guardian_swarm import GuardianSwarm
from core.action_engine import ActionEngine
from core.executive_summary import build_summary
from core.rfdc_math import (
    compute_entropy_from_events,
    compute_activity_concentration,
    compute_cross_pulse_proxy,
    compute_signal_pressure,
    compute_relational_gravity_proxy,
    compute_criticality,
    compute_homeostasis_proxy,
    compute_wave_risk,
    compute_nhi,
    compute_tpi,
    compute_scr,
    compute_climate_pressure,
    compute_vortex_score
)

class RelationalFieldDynamicsCore:
    def __init__(self):
        self.detector = FraudDetectionEngine()
        self.dark = RelationalDarkMatter()
        self.wave = RelationalWaveEngine()
        self.evolution = FraudEvolutionEngine()
        self.swarm = GuardianSwarm()
        self.action_engine = ActionEngine()

    def run(self, events_df: pd.DataFrame, signals_df: pd.DataFrame) -> dict:
        alerts_df = self.detector.detect(events_df, signals_df)
        alerts = alerts_df.to_dict(orient="records") if not alerts_df.empty else []

        mdi = self.dark.compute_mdi(events_df) if not events_df.empty else 0
        hidden_clusters = self.dark.detect_hidden_clusters(events_df) if not events_df.empty else []
        waves = self.wave.propagate(events_df) if not events_df.empty else []
        wave_summary = {
            "count": len(waves),
            "max_wave": round(max(waves), 3) if waves else 0,
            "avg_wave": round(sum(waves) / len(waves), 3) if waves else 0,
        }

        entropy = compute_entropy_from_events(events_df)
        concentration = compute_activity_concentration(events_df)
        cross_pulse = compute_cross_pulse_proxy(events_df)
        signal_pressure = compute_signal_pressure(signals_df)
        gravity = compute_relational_gravity_proxy(events_df)
        criticality = compute_criticality(entropy, concentration, mdi, wave_summary["avg_wave"], len(hidden_clusters))
        climate_pressure = compute_climate_pressure(signal_pressure, criticality, gravity)
        vortex_score = compute_vortex_score(len(hidden_clusters), concentration, cross_pulse)
        wave_risk = compute_wave_risk(wave_summary["max_wave"], wave_summary["avg_wave"])
        tpi = compute_tpi(signal_pressure, mdi, len(hidden_clusters), cross_pulse)
        nhi = compute_nhi(entropy, gravity, tpi, mdi)
        scr = compute_scr(nhi, tpi, criticality, climate_pressure, wave_risk)
        homeostasis = compute_homeostasis_proxy(nhi, tpi, scr)

        seed_pattern = self.evolution.generate_pattern()
        mutated_pattern = self.evolution.mutate_pattern(seed_pattern.copy())

        norm_alerts = []
        for a in alerts:
            score = a.get("score", 0)
            norm_score = min(1.0, float(score) / 100.0) if isinstance(score, (int, float)) else 0.0
            item = dict(a)
            item["score"] = norm_score
            norm_alerts.append(item)
        validated = self.swarm.validate(norm_alerts)

        metrics = {
            "nhi": round(nhi, 3),
            "tpi": round(tpi, 3),
            "scr": round(scr, 3),
            "mdi": round(mdi, 3),
            "entropy": round(entropy, 4),
            "gravity": round(gravity, 3),
            "cross_pulse": round(cross_pulse, 4),
            "criticality": round(criticality, 3),
            "climate_pressure": round(climate_pressure, 3),
            "vortex_score": round(vortex_score, 3),
            "homeostasis": round(homeostasis, 3),
            "wave_count": wave_summary["count"],
            "wave_max": wave_summary["max_wave"],
            "wave_avg": wave_summary["avg_wave"],
            "hidden_cluster_count": len(hidden_clusters),
            "validated_alert_count": len(validated),
        }

        if scr < 20:
            metrics["band"] = "stable"
            metrics["message"] = "No systemic stress pattern detected."
        elif scr < 45:
            metrics["band"] = "watch"
            metrics["message"] = "Early systemic pressure detected."
        elif scr < 70:
            metrics["band"] = "warning"
            metrics["message"] = "System approaching criticality."
        else:
            metrics["band"] = "collapse_risk"
            metrics["message"] = "Cascade / collapse risk elevated."

        decision = self.action_engine.decide(metrics, alerts, validated)
        summary = build_summary(metrics, decision, alerts)

        return {
            "decision": decision,
            "summary": summary,
            "alerts": alerts,
            "validated_alerts": validated,
            "metrics": metrics,
            "hidden_clusters": hidden_clusters[:25],
            "wave_summary": wave_summary,
            "evolution": {
                "seed_pattern": seed_pattern,
                "mutated_pattern": mutated_pattern
            }
        }
