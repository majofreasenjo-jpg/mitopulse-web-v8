import pandas as pd
import numpy as np

class SystemicCollapsePredictor:
    def __init__(self):
        pass

    def compute_metrics(self, events_df: pd.DataFrame, signals_df: pd.DataFrame) -> dict:
        # Safe defaults
        if events_df.empty and signals_df.empty:
            return {
                "nhi": 85.0,
                "tpi": 5.0,
                "scr": 4.0,
                "entropy": 0.0,
                "criticality": 0.0,
                "climate_pressure": 0.0,
                "vortex_score": 0.0,
            }

        # Entropy proxy from event_type distribution
        if not events_df.empty and "event_type" in events_df.columns:
            probs = events_df["event_type"].value_counts(normalize=True)
            entropy = float(-(probs * np.log(probs + 1e-9)).sum())
        else:
            entropy = 0.0

        # Threat Pressure proxy
        if not signals_df.empty and "severity" in signals_df.columns:
            severity_mean = float(pd.to_numeric(signals_df["severity"], errors="coerce").fillna(0).mean())
            signal_count = float(len(signals_df))
        else:
            severity_mean = 0.0
            signal_count = 0.0

        # Gravity / concentration proxy from source frequency
        if not events_df.empty and "source_id" in events_df.columns:
            freq = events_df["source_id"].astype(str).value_counts(normalize=True)
            concentration = float(freq.iloc[0]) if len(freq) else 0.0
            coordination = float((freq > 0.08).sum())
        else:
            concentration = 0.0
            coordination = 0.0

        tpi = min(100.0, severity_mean * 70.0 + min(signal_count / 5.0, 25.0) + coordination * 2.5)
        criticality = min(100.0, entropy * 25.0 + concentration * 100.0 + coordination * 3.0)
        climate_pressure = min(100.0, tpi * 0.55 + criticality * 0.45)
        vortex_score = min(100.0, coordination * 5.0 + concentration * 80.0)
        nhi = max(0.0, 100.0 - (entropy * 18.0 + tpi * 0.45 + concentration * 35.0))
        scr = min(100.0, (100.0 - nhi) * 0.35 + tpi * 0.35 + criticality * 0.2 + climate_pressure * 0.1)

        return {
            "nhi": round(nhi, 2),
            "tpi": round(tpi, 2),
            "scr": round(scr, 2),
            "entropy": round(entropy, 4),
            "criticality": round(criticality, 2),
            "climate_pressure": round(climate_pressure, 2),
            "vortex_score": round(vortex_score, 2),
        }

    def run(self, events_df: pd.DataFrame, signals_df: pd.DataFrame) -> dict:
        metrics = self.compute_metrics(events_df, signals_df)
        scr = metrics["scr"]
        if scr < 20:
            band = "stable"
            message = "No systemic stress pattern detected."
        elif scr < 45:
            band = "watch"
            message = "Early systemic pressure detected."
        elif scr < 70:
            band = "warning"
            message = "System approaching criticality."
        else:
            band = "collapse_risk"
            message = "Cascade / collapse risk elevated."
        metrics["band"] = band
        metrics["message"] = message
        return metrics
