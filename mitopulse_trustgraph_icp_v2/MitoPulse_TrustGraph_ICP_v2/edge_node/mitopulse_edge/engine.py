
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import time, json, base64, math
import numpy as np
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

def clamp(x, lo, hi): return max(lo, min(hi, x))

@dataclass
class Signals:
    hr: float
    hrv_rmssd: Optional[float]=None
    spo2: Optional[float]=None
    sleep_score: Optional[float]=None
    load: Optional[float]=None
    tap_rate: Optional[float]=None
    keystroke_var: Optional[float]=None

@dataclass
class Env:
    altitude_m: Optional[float]=None
    temp_c: Optional[float]=None
    humidity_pct: Optional[float]=None
    pressure_hpa: Optional[float]=None

def canonical_json(obj) -> bytes:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")

def sha256_hex(b: bytes) -> str:
    import hashlib
    return hashlib.sha256(b).hexdigest()

def tier_from_signals(s: Signals) -> str:
    if s.hrv_rmssd is None and s.spo2 is None and s.tap_rate is not None:
        return "tier0"
    if s.hrv_rmssd is None:
        return "tier1"
    return "tier2"

def compute_c_env(e: Env) -> float:
    a = (e.altitude_m or 0.0)/1000.0
    t = abs((e.temp_c if e.temp_c is not None else 22.0)-22.0)
    h = abs((e.humidity_pct if e.humidity_pct is not None else 50.0)-50.0)/50.0
    p = abs((e.pressure_hpa if e.pressure_hpa is not None else 1013.25)-1013.25)/200.0
    raw = 1.0/(1.0 + 0.012*a + 0.008*t + 0.005*h + 0.004*p)
    return clamp(raw, 0.85, 1.15)

def normalize_hr(hr): return clamp(1.0 - (hr-40.0)/140.0, 0.0, 1.0)
def normalize_hrv(hrv): return clamp((hrv-10.0)/110.0, 0.0, 1.0)
def normalize_spo2(spo2): return clamp(spo2, 0.0, 1.0)
def normalize_sleep(s): return clamp(s, 0.0, 1.0)
def normalize_load(l): return clamp(1.0 - l/10.0, 0.0, 1.0)

def normalize_interaction(tap_rate: float, keystroke_var: Optional[float]) -> float:
    tr = clamp(1.0 - abs(tap_rate-20.0)/40.0, 0.0, 1.0)
    kv = clamp((keystroke_var or 0.3), 0.0, 1.0)
    return clamp(0.7*tr + 0.3*kv, 0.0, 1.0)

def compute_index_risk_human(s: Signals, c_env: float) -> Tuple[float,int,bool,float]:
    b_hr = normalize_hr(s.hr)
    b_sleep = normalize_sleep(s.sleep_score or 0.6)
    b_load = normalize_load(s.load or 2.0)
    b_hrv = normalize_hrv(s.hrv_rmssd) if s.hrv_rmssd is not None else None
    b_spo2 = normalize_spo2(s.spo2) if s.spo2 is not None else None

    if b_hrv is None and b_spo2 is None and s.tap_rate is not None:
        b_int = normalize_interaction(s.tap_rate, s.keystroke_var)
        fused = 0.45*b_hr + 0.35*b_sleep + 0.20*b_int
    elif b_hrv is None:
        fused = 0.50*b_hr + 0.25*b_sleep + 0.25*(b_spo2 or 0.6)
    else:
        fused = 0.40*b_hr + 0.35*b_hrv + 0.15*b_sleep + 0.10*(b_spo2 or 0.7)

    idx = clamp(fused*c_env, 0.0, 1.0)
    risk = int(clamp((1.0-idx)*100.0, 0.0, 100.0))
    if s.hrv_rmssd is not None and s.hrv_rmssd < 25: risk = min(100, risk+15)
    if s.spo2 is not None and s.spo2 < 0.93: risk = min(100, risk+15)
    if s.sleep_score is not None and s.sleep_score < 0.4: risk = min(100, risk+10)
    coercion = risk >= 80
    human_conf = clamp(0.55 + 0.45*idx, 0.0, 1.0)
    return idx, risk, coercion, human_conf

class TemporalWindow:
    def __init__(self, days: int = 60):
        self.days = days
        self.points = []  # (ts, idx)

    def add(self, ts: int, idx: float):
        self.points.append((ts, idx))
        cutoff = ts - self.days*24*3600
        self.points = [(t,x) for (t,x) in self.points if t >= cutoff]

    def slope(self) -> float:
        if len(self.points) < 2:
            return 0.0
        xs = np.array([(t - self.points[0][0]) / 86400.0 for (t,_) in self.points], dtype=float)
        ys = np.array([x for (_,x) in self.points], dtype=float)
        # simple linear regression slope
        denom = float(np.sum((xs - xs.mean())**2))
        if denom < 1e-9:
            return 0.0
        m = float(np.sum((xs - xs.mean())*(ys - ys.mean())) / denom)
        return m

class EdgeNode:
    def __init__(self, tenant_id: str, user_id: str, device_id: str, epoch: int, priv: Ed25519PrivateKey):
        self.tenant_id=tenant_id
        self.user_id=user_id
        self.device_id=device_id
        self.epoch=epoch
        self.priv=priv
        self.window=TemporalWindow(days=60)

    def pubkey_b64(self) -> str:
        pub = self.priv.public_key().public_bytes_raw()
        return base64.b64encode(pub).decode("utf-8")

    def build_packet(self, signals: Signals, env: Env, request_id: str, ts: Optional[int]=None) -> Dict[str,Any]:
        ts = int(ts or time.time())
        tier = tier_from_signals(signals)
        c_env = compute_c_env(env)
        idx, risk, coercion, human_conf = compute_index_risk_human(signals, c_env)
        self.window.add(ts, idx)
        slope = self.window.slope()

        # stability is computed on server using baselines; here we emit a placeholder (client-side quick estimate)
        stability = clamp(0.2 + 0.8*idx, 0.0, 1.0)

        payload = {
            "version":"2.0",
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "device_id": self.device_id,
            "epoch": int(self.epoch),
            "ts": ts,
            "tier": tier,
            "signals": {
                "hr": float(signals.hr),
                "hrv_rmssd": signals.hrv_rmssd,
                "spo2": signals.spo2,
                "sleep_score": signals.sleep_score,
                "load": signals.load,
                "tap_rate": signals.tap_rate,
                "keystroke_var": signals.keystroke_var
            },
            "env": {
                "altitude_m": env.altitude_m,
                "temp_c": env.temp_c,
                "humidity_pct": env.humidity_pct,
                "pressure_hpa": env.pressure_hpa
            },
            "idx": float(idx),
            "slope": float(slope),
            "stability": float(stability),
            "human_conf": float(human_conf),
            "risk": int(risk),
            "coercion": bool(coercion),
            "request_id": request_id
        }
        msg = canonical_json(payload)
        sig = self.priv.sign(msg)
        payload["sig_b64"] = base64.b64encode(sig).decode("utf-8")
        return payload
