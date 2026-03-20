import pandas as pd
from core.fraud_detection_engine import FraudDetectionEngine
from core.systemic_collapse_predictor import SystemicCollapsePredictor
from core.relational_dark_matter import RelationalDarkMatter
from core.relational_wave_engine import RelationalWaveEngine
from core.fraud_evolution_engine import FraudEvolutionEngine
from core.guardian_swarm import GuardianSwarm

class RelationalFieldDynamicsCore:
    def __init__(self):
        self.detector = FraudDetectionEngine()
        self.collapse = SystemicCollapsePredictor()
        self.dark = RelationalDarkMatter()
        self.wave = RelationalWaveEngine()
        self.evolution = FraudEvolutionEngine()
        self.swarm = GuardianSwarm()

    def run(self, events_df: pd.DataFrame, signals_df: pd.DataFrame) -> dict:
        # Detection
        alerts_df = self.detector.detect(events_df, signals_df)
        alerts = alerts_df.to_dict(orient="records") if not alerts_df.empty else []

        # Dark matter + MDI
        mdi = self.dark.compute_mdi(events_df) if not events_df.empty else 0
        hidden_clusters = self.dark.detect_hidden_clusters(events_df) if not events_df.empty else []

        # Relational waves
        waves = self.wave.propagate(events_df) if not events_df.empty else []
        wave_summary = {
            "count": len(waves),
            "max_wave": round(max(waves), 3) if waves else 0,
            "avg_wave": round(sum(waves) / len(waves), 3) if waves else 0,
        }

        # Systemic metrics
        systemic = self.collapse.run(events_df, signals_df)

        # Fraud evolution sample
        seed_pattern = self.evolution.generate_pattern()
        mutated_pattern = self.evolution.mutate_pattern(seed_pattern.copy())

        # Guardian validation (normalize scores for v1)
        norm_alerts = []
        for a in alerts:
            score = a.get("score", 0)
            norm_score = min(1.0, float(score) / 100.0) if isinstance(score, (int, float)) else 0.0
            item = dict(a)
            item["score"] = norm_score
            norm_alerts.append(item)
        validated = self.swarm.validate(norm_alerts)

        # enrich systemic metrics with mdi / waves
        metrics = dict(systemic)
        metrics["mdi"] = mdi
        metrics["wave_count"] = wave_summary["count"]
        metrics["wave_max"] = wave_summary["max_wave"]
        metrics["wave_avg"] = wave_summary["avg_wave"]

        return {
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
