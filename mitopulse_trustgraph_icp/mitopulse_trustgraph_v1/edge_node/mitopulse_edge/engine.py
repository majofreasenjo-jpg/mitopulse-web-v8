from __future__ import annotations

import json
import time
import uuid
import base64
import hmac
import hashlib
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple

import numpy as np


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def hmac_sha256_b64(secret_b64: str, message: bytes) -> str:
    key = base64.b64decode(secret_b64)
    mac = hmac.new(key, message, hashlib.sha256).digest()
    return b64url(mac)


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
    humidity: Optional[float] = None
    pressure_hpa: Optional[float] = None


class RollingWindow:
    def __init__(self, max_points: int = 90):
        self.max_points = max_points
        self.values: list[float] = []

    def push(self, x: float) -> None:
        self.values.append(float(x))
        if len(self.values) > self.max_points:
            self.values = self.values[-self.max_points :]

    def vector(self) -> Dict[str, float]:
        if not self.values:
            return {"mean": 0.0, "std": 0.0, "slope": 0.0}
        arr = np.array(self.values, dtype=float)
        mean = float(arr.mean())
        std = float(arr.std())
        slope = 0.0
        if len(arr) >= 3:
            x = np.arange(len(arr), dtype=float)
            slope = float(np.polyfit(x, arr, 1)[0])
        return {"mean": mean, "std": std, "slope": slope}


def tier_from_signals(s: Signals) -> str:
    # Tier0: no wearable signals
    if s.hr is None and s.spo2 is None and s.hrv_rmssd is None:
        return "tier0"
    if s.hrv_rmssd is not None:
        return "tier2"
    # tier1: phone-level signals
    if s.hr is not None or s.spo2 is not None:
        return "tier1"
    return "tier0"


def compute_index(s: Signals, e: Env) -> float:
    """Simple proxy index 0..1. Deterministic and tier-agnostic."""
    # normalize helpers
    def clamp01(x: float) -> float:
        return max(0.0, min(1.0, x))

    # HR: lower is better (rest)
    hr = s.hr if s.hr is not None else 75.0
    hr_n = clamp01(1.0 - (hr - 50.0) / 80.0)

    # HRV: higher better
    hrv = s.hrv_rmssd if s.hrv_rmssd is not None else 30.0
    hrv_n = clamp01((hrv - 10.0) / 70.0)

    spo2 = s.spo2 if s.spo2 is not None else 97.0
    spo2_n = clamp01((spo2 - 90.0) / 10.0)

    sleep = s.sleep_score if s.sleep_score is not None else 70.0
    sleep_n = clamp01((sleep - 40.0) / 60.0)

    load = s.load if s.load is not None else 0.3
    load_n = clamp01(1.0 - load)

    # weighted fusion
    f = 0.28 * hr_n + 0.22 * hrv_n + 0.18 * spo2_n + 0.18 * sleep_n + 0.14 * load_n

    # environmental compensation 0.85..1.15
    alt = e.altitude_m or 0.0
    temp = e.temp_c if e.temp_c is not None else 22.0
    hum = e.humidity if e.humidity is not None else 50.0

    c_env = 1.0 / (1.0 + 0.012 * (alt / 1000.0) + 0.008 * abs(temp - 22.0) + 0.005 * abs(hum - 50.0))
    c_env = max(0.85, min(1.15, c_env))

    return float(max(0.0, min(1.0, f * c_env)))


def risk_and_coercion(s: Signals, index_value: float, vec: Dict[str, float]) -> Tuple[int, bool, float, float]:
    """Heurísticas: riesgo sube con HR alto, HRV bajo, slope negativo. Stability y human_conf 0..1."""
    hr = s.hr if s.hr is not None else 75.0
    hrv = s.hrv_rmssd if s.hrv_rmssd is not None else 30.0

    slope = vec.get("slope", 0.0)
    risk = 0
    risk += int(max(0, (hr - 85) * 0.8))
    risk += int(max(0, (25 - hrv) * 1.2))
    if slope < -0.01:
        risk += int(min(25, abs(slope) * 900))
    if index_value < 0.22:
        risk += 20
    risk = max(0, min(100, risk))

    coercion = risk >= 85 or (index_value < 0.15 and hr > 95)

    # stability: probability that current index is near window mean
    mean = vec.get("mean", index_value)
    std = max(0.03, vec.get("std", 0.05))
    z = abs(index_value - mean) / std
    stability = float(max(0.0, min(1.0, np.exp(-0.5 * z * z))))

    # human_conf: penalize too-perfect signals (low variability) + impossible combos
    human_conf = 0.85
    if vec.get("std", 0.0) < 0.005 and len(vec) > 0:
        human_conf -= 0.2
    if s.spo2 is not None and s.spo2 < 85:
        human_conf -= 0.2
    if s.hr is not None and s.hr < 35:
        human_conf -= 0.2
    human_conf = float(max(0.0, min(1.0, human_conf)))

    return risk, coercion, stability, human_conf


def build_proof_packet(
    *,
    tenant_id: str,
    user_id: str,
    device_id: str,
    epoch: int,
    secret_b64: str,
    window: RollingWindow,
    signals: Signals,
    env: Env,
    context_fp: Optional[str] = None,
    ts: Optional[int] = None,
) -> Dict[str, Any]:
    ts = ts or int(time.time())
    tier = tier_from_signals(signals)
    idx = compute_index(signals, env)
    window.push(idx)
    vec = window.vector()

    # dynamic_id derived from temporal vector (serialized)
    vec_bytes = json.dumps(vec, separators=(",", ":")).encode("utf-8")
    dynamic_id = hmac_sha256_b64(secret_b64, vec_bytes)

    risk, coercion, stability, human_conf = risk_and_coercion(signals, idx, vec)

    payload = {
        "tenant_id": tenant_id,
        "user_id": user_id,
        "device_id": device_id,
        "epoch": epoch,
        "ts": ts,
        "tier_used": tier,
        "index_value": round(idx, 6),
        "dynamic_id": dynamic_id,
        "risk": risk,
        "coercion": coercion,
        "stability": round(stability, 6),
        "human_conf": round(human_conf, 6),
        "context_fp": context_fp,
        # NOTE: do not include raw signals in payload for prototype.
        "proof": {
            "vec": vec,
            "tier": tier,
        },
    }

    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    sig = hmac_sha256_b64(secret_b64, payload_bytes)

    packet = {
        "tenant_id": tenant_id,
        "user_id": user_id,
        "device_id": device_id,
        "epoch": epoch,
        "request_id": str(uuid.uuid4()),
        "ts": ts,
        "tier_used": tier,
        "index_value": payload["index_value"],
        "dynamic_id": dynamic_id,
        "risk": risk,
        "coercion": coercion,
        "stability": payload["stability"],
        "human_conf": payload["human_conf"],
        "context_fp": context_fp,
        "payload": payload,
        "sig": sig,
    }
    return packet


def build_icp_start_payload(tenant_id: str, user_id: str, old_device_id: str, new_device_id: str, ts: Optional[int] = None) -> Dict[str, Any]:
    return {
        "tenant_id": tenant_id,
        "user_id": user_id,
        "old_device_id": old_device_id,
        "new_device_id": new_device_id,
        "ts": ts or int(time.time()),
        "purpose": "icp_handoff_start",
    }


def build_icp_complete_payload(tenant_id: str, user_id: str, new_device_id: str, handoff_token: str, ts: Optional[int] = None) -> Dict[str, Any]:
    return {
        "tenant_id": tenant_id,
        "user_id": user_id,
        "new_device_id": new_device_id,
        "handoff_token": handoff_token,
        "ts": ts or int(time.time()),
        "purpose": "icp_handoff_complete",
    }
