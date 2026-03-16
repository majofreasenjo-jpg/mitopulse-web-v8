
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import math
import hmac
import hashlib
import json
import base64

def clamp(x: float, lo: float=0.0, hi: float=1.0) -> float:
    return max(lo, min(hi, x))

@dataclass
class Signals:
    hr: Optional[float] = None
    hrv_rmssd: Optional[float] = None
    spo2: Optional[float] = None
    sleep_score: Optional[float] = None
    load: Optional[float] = None

@dataclass
class Env:
    altitude_m: Optional[float] = None
    temp_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    pressure_hpa: Optional[float] = None

def select_tier(sig: Signals) -> str:
    if sig.hrv_rmssd is not None and sig.spo2 is not None:
        return "tier3"
    if sig.hrv_rmssd is not None:
        return "tier2"
    return "tier1"

def env_comp(env: Env) -> float:
    alt = env.altitude_m if env.altitude_m is not None else 0.0
    t = env.temp_c if env.temp_c is not None else 22.0
    h = env.humidity_pct if env.humidity_pct is not None else 50.0
    p = env.pressure_hpa if env.pressure_hpa is not None else 1013.25
    penalty = 0.0
    penalty += 0.012 * (alt / 1000.0)
    penalty += 0.008 * abs(t - 22.0)
    penalty += 0.005 * abs(h - 50.0) / 50.0
    penalty += 0.002 * abs(p - 1013.25) / 100.0
    c = 1.0 / (1.0 + penalty)
    return clamp(c, 0.85, 1.15)

def normalize(sig: Signals) -> Dict[str, float]:
    out: Dict[str, float] = {}
    if sig.hr is not None:
        out["hr"] = clamp((sig.hr - 40.0) / 140.0)
    if sig.hrv_rmssd is not None:
        out["hrv"] = clamp((sig.hrv_rmssd - 10.0) / 110.0)
    if sig.spo2 is not None:
        out["spo2"] = clamp((sig.spo2 - 85.0) / 15.0)
    if sig.sleep_score is not None:
        out["sleep"] = clamp(sig.sleep_score / 100.0)
    if sig.load is not None:
        out["load"] = clamp(sig.load / 10.0)
    return out

def fuse(norm: Dict[str,float], tier: str) -> float:
    hr = norm.get("hr", 0.5)
    hrv = norm.get("hrv", 0.5)
    spo2 = norm.get("spo2", 0.7)
    sleep = norm.get("sleep", 0.7)
    load = norm.get("load", 0.2)
    if tier == "tier1":
        return clamp(0.45*(1-hr) + 0.35*(1-load) + 0.20*sleep)
    if tier == "tier2":
        return clamp(0.35*(1-hr) + 0.30*hrv + 0.20*spo2 + 0.15*sleep)
    return clamp(0.30*(1-hr) + 0.30*hrv + 0.25*spo2 + 0.15*sleep)

def compute_index(sig: Signals, env: Env, K: float=1.0) -> Tuple[float,str,float]:
    tier = select_tier(sig)
    norm = normalize(sig)
    cenv = env_comp(env)
    idx = K * fuse(norm, tier) * cenv
    return (clamp(idx), tier, cenv)

def compute_risk(sig: Signals, idx: float) -> Tuple[int,bool]:
    risk = 0.0
    if sig.hr is not None and sig.hr > 120:
        risk += 25
    if sig.hrv_rmssd is not None and sig.hrv_rmssd < 20:
        risk += 25
    if sig.spo2 is not None and sig.spo2 < 92:
        risk += 25
    if idx < 0.20:
        risk += 30
    risk = clamp(risk/100.0) * 100
    return int(round(risk)), risk >= 70

def stability_score(idx: float, baseline_idx: float, baseline_std: float) -> float:
    sigma = max(baseline_std, 0.05)
    z = abs(idx - baseline_idx) / sigma
    return clamp(math.exp(-z))

def human_confidence(sig: Signals, idx: float, prev: Optional[Dict[str,Any]]=None) -> float:
    score = 0.7
    if sig.hr is not None and sig.load is not None:
        if sig.hr > 130 and sig.load < 0.5:
            score -= 0.25
        if sig.hr < 50 and sig.load > 6:
            score -= 0.20
    if sig.hrv_rmssd is not None and sig.hr is not None:
        if sig.hr > 120 and sig.hrv_rmssd > 80:
            score -= 0.25
    if prev:
        try:
            delta = abs(idx - float(prev.get("index", idx)))
            score += 0.05 if delta > 0.001 else -0.15
        except Exception:
            pass
    return clamp(score)

def _urlsafe_b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("utf-8").rstrip("=")

def dynamic_id_hmac(secret: bytes, vector: Dict[str,Any]) -> str:
    payload = json.dumps(vector, sort_keys=True, separators=(",",":")).encode("utf-8")
    mac = hmac.new(secret, payload, hashlib.sha256).digest()
    return _urlsafe_b64(mac)

def sign_payload(secret: bytes, payload: Dict[str,Any]) -> str:
    pb = json.dumps(payload, sort_keys=True, separators=(",",":")).encode("utf-8")
    mac = hmac.new(secret, pb, hashlib.sha256).digest()
    return _urlsafe_b64(mac)
