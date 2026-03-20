import math
import pandas as pd

def compute_entropy_from_events(events_df: pd.DataFrame) -> float:
    if events_df.empty or "event_type" not in events_df.columns:
        return 0.0
    probs = events_df["event_type"].astype(str).value_counts(normalize=True)
    return float(-(probs * (probs + 1e-12).apply(math.log)).sum())

def compute_activity_concentration(events_df: pd.DataFrame) -> float:
    if events_df.empty or "source_id" not in events_df.columns:
        return 0.0
    freq = events_df["source_id"].astype(str).value_counts(normalize=True)
    return float(freq.iloc[0]) if len(freq) else 0.0

def compute_cross_pulse_proxy(events_df: pd.DataFrame) -> float:
    if events_df.empty or "timestamp" not in events_df.columns:
        return 0.0
    counts = events_df.groupby("timestamp")["source_id"].nunique()
    if counts.empty:
        return 0.0
    burstiness = float((counts > counts.mean()).sum() / max(len(counts), 1))
    return round(min(1.0, burstiness * 1.5), 4)

def compute_signal_pressure(signals_df: pd.DataFrame) -> float:
    if signals_df.empty or "severity" not in signals_df.columns:
        return 0.0
    sev = pd.to_numeric(signals_df["severity"], errors="coerce").fillna(0)
    mean_sev = float(sev.mean())
    return round(min(100.0, mean_sev * 70.0 + len(signals_df) * 0.25), 3)

def compute_relational_gravity_proxy(events_df: pd.DataFrame) -> float:
    if events_df.empty or "source_id" not in events_df.columns:
        return 0.0
    freq = events_df["source_id"].astype(str).value_counts(normalize=True)
    top5 = float(freq.head(5).sum()) if len(freq) else 0.0
    return round(min(100.0, top5 * 100.0), 3)

def compute_criticality(entropy: float, concentration: float, mdi: float, wave_avg: float, hidden_clusters: int) -> float:
    raw = entropy * 22.0 + concentration * 90.0 + mdi * 0.35 + wave_avg * 0.015 + hidden_clusters * 3.5
    return round(min(100.0, raw), 3)

def compute_homeostasis_proxy(nhi: float, tpi: float, scr: float) -> float:
    value = max(0.0, 100.0 - abs(50.0 - nhi) * 0.8 - tpi * 0.25 - scr * 0.2)
    return round(value, 3)

def compute_wave_risk(max_wave: float, avg_wave: float) -> float:
    return round(min(100.0, max_wave * 0.01 + avg_wave * 0.03), 3)

def compute_nhi(entropy: float, gravity: float, tpi: float, mdi: float) -> float:
    nhi = 100.0 - (entropy * 18.0 + gravity * 0.18 + tpi * 0.35 + mdi * 0.15)
    return round(max(0.0, min(100.0, nhi)), 3)

def compute_tpi(signal_pressure: float, mdi: float, hidden_clusters: int, cross_pulse: float) -> float:
    tpi = signal_pressure * 0.55 + mdi * 0.18 + hidden_clusters * 2.8 + cross_pulse * 18.0
    return round(max(0.0, min(100.0, tpi)), 3)

def compute_scr(nhi: float, tpi: float, criticality: float, climate_pressure: float, wave_risk: float) -> float:
    scr = (100.0 - nhi) * 0.32 + tpi * 0.28 + criticality * 0.18 + climate_pressure * 0.14 + wave_risk * 0.08
    return round(max(0.0, min(100.0, scr)), 3)

def compute_climate_pressure(tpi: float, criticality: float, gravity: float) -> float:
    pressure = tpi * 0.45 + criticality * 0.35 + gravity * 0.20
    return round(max(0.0, min(100.0, pressure)), 3)

def compute_vortex_score(hidden_clusters: int, concentration: float, cross_pulse: float) -> float:
    score = hidden_clusters * 4.5 + concentration * 70.0 + cross_pulse * 20.0
    return round(max(0.0, min(100.0, score)), 3)
