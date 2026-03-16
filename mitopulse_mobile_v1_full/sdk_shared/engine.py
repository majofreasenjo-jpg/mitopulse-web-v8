from __future__ import annotations
import hmac, json, base64
from dataclasses import dataclass
from hashlib import sha256
from typing import Optional, List, Dict, Any, Tuple

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

@dataclass
class Sample:
    ts: int
    hr: float
    hrv_rmssd: Optional[float]=None
    spo2: Optional[float]=None
    sleep_score: Optional[float]=None
    accel_load: Optional[float]=None
    altitude_m: Optional[float]=None
    temp_c: Optional[float]=None
    humidity: Optional[float]=None

def select_tier(s: Sample) -> str:
    has_basic = (s.spo2 is not None or s.sleep_score is not None or s.accel_load is not None)
    if has_basic and s.hrv_rmssd is not None: return "tier2"
    return "tier1"

def c_env(s: Sample) -> float:
    if s.altitude_m is None and s.temp_c is None and s.humidity is None:
        return 1.0
    alt = (s.altitude_m or 0.0)/1000.0
    t = s.temp_c if s.temp_c is not None else 22.0
    h = s.humidity if s.humidity is not None else 50.0
    v = 1.0/(1.0 + 0.012*alt + 0.008*abs(t-22.0) + 0.005*abs(h-50.0)/50.0)
    return clamp(v, 0.85, 1.15)

def normalize(s: Sample) -> Dict[str,float]:
    hr = clamp(1.0 - (s.hr-50.0)/80.0, 0.0, 1.0)
    out = {"hr": hr}
    if s.hrv_rmssd is not None: out["hrv"] = clamp((s.hrv_rmssd-10.0)/90.0, 0.0, 1.0)
    if s.spo2 is not None: out["spo2"] = clamp((s.spo2-90.0)/10.0, 0.0, 1.0)
    if s.sleep_score is not None: out["sleep"] = clamp(s.sleep_score/100.0, 0.0, 1.0)
    if s.accel_load is not None: out["load"] = clamp(1.0 - s.accel_load/10.0, 0.0, 1.0)
    return out

def mitopulse_index(s: Sample) -> Tuple[float,str]:
    tier = select_tier(s)
    b = normalize(s)
    w = {"hr":0.30,"hrv":0.30,"spo2":0.20,"sleep":0.10,"load":0.10} if tier=="tier2" else {"hr":0.40,"spo2":0.25,"sleep":0.20,"load":0.15}
    acc=0.0; tw=0.0
    for k,wk in w.items():
        if k in b:
            acc += wk*b[k]; tw += wk
    base = 0.5 if tw<=0 else acc/tw
    idx = clamp(base*c_env(s), 0.0, 1.0)
    return idx, tier

def vectorize(history: List[float]) -> Dict[str,float]:
    if not history: return {"mean":0.0,"last":0.0,"slope":0.0}
    mean = sum(history)/len(history)
    last = history[-1]
    slope = history[-1]-history[-2] if len(history)>=2 else 0.0
    return {"mean":mean,"last":last,"slope":slope}

def dynamic_id(secret: bytes, vector: Dict[str,float]) -> str:
    payload = json.dumps(vector, sort_keys=True, separators=(',',':')).encode()
    sig = hmac.new(secret, payload, sha256).digest()
    return base64.urlsafe_b64encode(sig).decode().rstrip('=')

def risk_score(s: Sample, idx: float, slope: float) -> Tuple[int,bool]:
    risk=0
    if idx < 0.25: risk += 50
    if slope < -0.05: risk += 20
    if s.hrv_rmssd is not None and s.hrv_rmssd < 20: risk += 20
    if s.hr > 110: risk += 20
    risk=int(clamp(risk,0,100))
    return risk, (risk>=75)
