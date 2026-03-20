import pandas as pd
import numpy as np

class FraudDetectionEngine:
    def __init__(self, velocity_threshold: float = 100.0, signal_threshold: float = 0.6):
        self.velocity_threshold = velocity_threshold
        self.signal_threshold = signal_threshold

    def _compute_velocity(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        out = df.copy()
        if "timestamp" in out.columns:
            out = out.sort_values("timestamp")
        out["delta"] = out["amount"].fillna(0).diff().fillna(0)
        out["abs_delta"] = out["delta"].abs()
        return out

    def detect(self, events_df: pd.DataFrame, signals_df: pd.DataFrame) -> pd.DataFrame:
        results = []

        if not events_df.empty:
            events_df = self._compute_velocity(events_df)

            for entity in events_df["source_id"].dropna().unique():
                subset = events_df[events_df["source_id"] == entity]
                if len(subset) < 3:
                    continue

                velocity = subset["abs_delta"].mean()
                intensity = subset["amount"].fillna(0).mean()
                score = float(velocity * max(intensity, 1) / 1000.0)

                if score > self.velocity_threshold:
                    results.append({
                        "entity": entity,
                        "type": "velocity_anomaly",
                        "score": round(score, 3),
                        "evidence": f"avg_abs_delta={round(velocity, 2)}, avg_amount={round(float(intensity), 2)}"
                    })

            if "timestamp" in events_df.columns:
                grouped = events_df.groupby("timestamp")
                for ts, group in grouped:
                    uniq_entities = list(group["source_id"].dropna().astype(str).unique())
                    if len(uniq_entities) >= 4:
                        results.append({
                            "entity": ",".join(uniq_entities[:12]),
                            "type": "shadow_coordination",
                            "score": int(len(uniq_entities)),
                            "evidence": f"synchronized_entities={len(uniq_entities)} at {ts}"
                        })

        if not signals_df.empty:
            for entity in signals_df["entity_id"].dropna().unique():
                subset = signals_df[signals_df["entity_id"] == entity]
                sev = float(subset["severity"].astype(float).mean())
                if sev > self.signal_threshold:
                    results.append({
                        "entity": entity,
                        "type": "high_signal_pressure",
                        "score": round(sev, 3),
                        "evidence": f"avg_severity={round(sev, 3)}"
                    })

        if not results:
            return pd.DataFrame(columns=["entity","type","score","evidence"])
        return pd.DataFrame(results).sort_values(["type","score"], ascending=[True, False])
