from __future__ import annotations
import base64, hashlib, hmac, json, math
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple, List

@dataclass
class Env:
    altitude_m: float = 0.0
    temp_c: float = 22.0
    humidity: float = 50.0
    pressure_hpa: float = 1013.25

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def normalize(x: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 0.5
    return clamp((x - lo) / (hi - lo), 0.0, 1.0)

def c_env(env: Env) -> float:
    # simple bounded environmental compensation (demo)
    alt = env.altitude_m / 1000.0
    t = abs(env.temp_c - 22.0)
    h = abs(env.humidity - 50.0) / 50.0
    p = abs(env.pressure_hpa - 1013.25) / 100.0
    raw = 1.0 / (1.0 + 0.012*alt + 0.008*t + 0.005*h + 0.003*p)
    return clamp(raw, 0.85, 1.15)

def pick_tier(signals: Dict[str, Any]) -> str:
    has_hrv = signals.get("hrv_rmssd") is not None
    has_spo2 = signals.get("spo2") is not None
    has_sleep = signals.get("sleep_score") is not None
    # Tier2 if HRV present; Tier1 otherwise; Tier3 placeholder
    if has_hrv:
        return "tier2"
    return "tier1"

def fused_index(signals: Dict[str, Any], env: Env) -> float:
    # MVP fusion (bounded 0..1)
    hr = signals.get("hr")
    hrv = signals.get("hrv_rmssd")
    spo2 = signals.get("spo2")
    sleep = signals.get("sleep_score")
    load = signals.get("accel_load")

    # normalize components (demo ranges)
    b_hr = 1.0 - normalize(float(hr or 75), 45, 140)   # lower HR better
    b_hrv = normalize(float(hrv or 25), 5, 120)        # higher HRV better
    b_spo2 = normalize(float(spo2 or 96), 85, 100)     # higher better
    b_sleep = normalize(float(sleep or 70), 0, 100)    # higher better
    b_load = 1.0 - normalize(float(load or 0.3), 0.0, 1.5)  # higher load reduces current score

    tier = pick_tier(signals)
    if tier == "tier1":
        # weights without HRV
        w = {"hr":0.35, "spo2":0.25, "sleep":0.20, "load":0.20}
        f = w["hr"]*b_hr + w["spo2"]*b_spo2 + w["sleep"]*b_sleep + w["load"]*b_load
    else:
        w = {"hr":0.25, "hrv":0.30, "spo2":0.20, "sleep":0.15, "load":0.10}
        f = w["hr"]*b_hr + w["hrv"]*b_hrv + w["spo2"]*b_spo2 + w["sleep"]*b_sleep + w["load"]*b_load

    idx = 1.0 * f * c_env(env)
    return clamp(idx, 0.0, 1.0)

def slope(values: List[float]) -> float:
    # simple slope over last N values (demo)
    n = len(values)
    if n < 2:
        return 0.0
    # linear regression slope with x=0..n-1
    xs = list(range(n))
    xbar = sum(xs)/n
    ybar = sum(values)/n
    num = sum((xs[i]-xbar)*(values[i]-ybar) for i in range(n))
    den = sum((xs[i]-xbar)**2 for i in range(n)) or 1.0
    return num/den

def risk_score(idx: float, s: float) -> Tuple[int, bool]:
    # heuristic: low idx + negative slope -> higher risk
    risk = 0
    if idx < 0.35: risk += 35
    if idx < 0.20: risk += 35
    if s < -0.05:  risk += 20
    if s < -0.10:  risk += 20
    risk = int(clamp(risk, 0, 100))
    coercion = risk >= 80 or idx < 0.12
    return risk, coercion

def serialize_vector(vec: Dict[str, Any]) -> bytes:
    # canonical json for HMAC
    return json.dumps(vec, sort_keys=True, separators=(",", ":")).encode("utf-8")

def dynamic_id(secret: bytes, vec: Dict[str, Any]) -> str:
    mac = hmac.new(secret, serialize_vector(vec), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).decode("utf-8").rstrip("=")

def compute_event(secret: bytes, ts: int, user_id: str, device_id: str, signals: Dict[str, Any], env: Env, history: List[float]) -> Dict[str, Any]:
    idx = fused_index(signals, env)
    hist = (history + [idx])[-60:]  # 60-day demo window
    s = slope(hist[-7:])  # 7-point slope window
    risk, coercion = risk_score(idx, s)
    tier = pick_tier(signals)

    vec = {
        "window_n": len(hist),
        "mean": sum(hist)/len(hist),
        "last": hist[-1],
        "std": (sum((x-(sum(hist)/len(hist)))**2 for x in hist)/len(hist))**0.5,
        "slope7": s,
        "tier": tier
    }
    dyn = dynamic_id(secret, vec)
    return {
        "ts": ts,
        "user_id": user_id,
        "device_id": device_id,
        "tier_used": tier,
        "index_value": float(idx),
        "slope": float(s),
        "risk": int(risk),
        "coercion": bool(coercion),
        "dynamic_id": dyn,
        "vector": vec,
        "history": hist,
    }
