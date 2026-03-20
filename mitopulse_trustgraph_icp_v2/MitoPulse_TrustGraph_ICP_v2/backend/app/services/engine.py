
from __future__ import annotations
from typing import Optional, Tuple
import math

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def tier_from_signals(hr: float, hrv: Optional[float], spo2: Optional[float], tap_rate: Optional[float]) -> str:
    # Tier0: no reliable physiology, only interaction proxies
    if hrv is None and spo2 is None and tap_rate is not None:
        return "tier0"
    # Tier1: phone sensors / partial
    if hrv is None:
        return "tier1"
    # Tier2: wearable HRV
    return "tier2"

def compute_c_env(altitude_m: Optional[float], temp_c: Optional[float], humidity_pct: Optional[float], pressure_hpa: Optional[float]) -> float:
    # simple bounded compensation; optional inputs
    a = (altitude_m or 0.0) / 1000.0
    t = abs((temp_c if temp_c is not None else 22.0) - 22.0)
    h = abs((humidity_pct if humidity_pct is not None else 50.0) - 50.0) / 50.0
    p = abs((pressure_hpa if pressure_hpa is not None else 1013.25) - 1013.25) / 200.0
    raw = 1.0 / (1.0 + 0.012*a + 0.008*t + 0.005*h + 0.004*p)
    return clamp(raw, 0.85, 1.15)

def normalize_hr(hr: float) -> float:
    # map 40..180 -> 1..0 (lower HR better)
    return clamp(1.0 - (hr-40.0)/140.0, 0.0, 1.0)

def normalize_hrv(hrv: float) -> float:
    # map 10..120 -> 0..1
    return clamp((hrv-10.0)/110.0, 0.0, 1.0)

def normalize_spo2(spo2: float) -> float:
    # spo2 already 0..1
    return clamp(spo2, 0.0, 1.0)

def normalize_sleep(sleep: float) -> float:
    return clamp(sleep, 0.0, 1.0)

def normalize_load(load: float) -> float:
    # map 0..10 -> 1..0 (less load -> better readiness)
    return clamp(1.0 - load/10.0, 0.0, 1.0)

def normalize_interaction(tap_rate: float, keystroke_var: Optional[float]) -> float:
    # simple proxy: stable, moderate activity indicates normal human use
    tr = clamp(1.0 - abs(tap_rate-20.0)/40.0, 0.0, 1.0) # 20 taps/min target
    kv = clamp((keystroke_var or 0.3), 0.0, 1.0)
    return clamp(0.7*tr + 0.3*kv, 0.0, 1.0)

def compute_index_and_risk(
    hr: float,
    hrv: Optional[float],
    spo2: Optional[float],
    sleep: Optional[float],
    load: Optional[float],
    tap_rate: Optional[float],
    keystroke_var: Optional[float],
    c_env: float,
) -> Tuple[float,int,bool,float]:
    # Basic weighted fusion per tier (MVP-friendly)
    b_hr = normalize_hr(hr)
    b_sleep = normalize_sleep(sleep or 0.6)
    b_load = normalize_load(load or 2.0)

    if hrv is not None:
        b_hrv = normalize_hrv(hrv)
    else:
        b_hrv = None

    if spo2 is not None:
        b_spo2 = normalize_spo2(spo2)
    else:
        b_spo2 = None

    if b_hrv is None and b_spo2 is None and tap_rate is not None:
        b_int = normalize_interaction(tap_rate, keystroke_var)
        fused = 0.45*b_hr + 0.35*b_sleep + 0.20*b_int
    elif b_hrv is None:
        fused = 0.50*b_hr + 0.25*b_sleep + 0.25*(b_spo2 or 0.6)
    else:
        fused = 0.40*b_hr + 0.35*b_hrv + 0.15*b_sleep + 0.10*(b_spo2 or 0.7)

    idx = clamp(fused * c_env, 0.0, 1.0)

    # risk heuristic: lower idx => higher risk; add penalties for low hrv/spo2/sleep
    risk = int(clamp((1.0-idx)*100.0, 0.0, 100.0))
    if hrv is not None and hrv < 25:
        risk = min(100, risk + 15)
    if spo2 is not None and spo2 < 0.93:
        risk = min(100, risk + 15)
    if sleep is not None and sleep < 0.4:
        risk = min(100, risk + 10)
    coercion = risk >= 80
    # human_conf: prefer "messy" but coherent signals; penalize too-perfect stability
    human_conf = clamp(0.55 + 0.45*idx, 0.0, 1.0)
    return idx, risk, coercion, human_conf

def compute_stability(z_hr: float, z_idx: float) -> float:
    # convert deviation to stability score (0..1) where 1 is stable
    d = math.sqrt(z_hr*z_hr + z_idx*z_idx)
    return clamp(math.exp(-0.8*d), 0.0, 1.0)
