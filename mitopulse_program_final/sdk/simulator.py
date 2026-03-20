"""MitoPulse Program Final – Full-Flow Simulator

Simulates the complete Watch → Phone → Backend pipeline:
  1. Watch generates HR samples (simulated)
  2. Phone engine computes index, tier, slope, anomaly score
  3. Client posts events + verifies against backend
  4. Anti-replay and tamper detection are tested
"""
from __future__ import annotations

import hashlib
import hmac
import base64
import json
import math
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

import requests


# ── Engine (Python port of the Kotlin engine from the .docx) ─────────

def clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def linear_norm(x: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 0.0
    return clamp((x - lo) / (hi - lo), 0.0, 1.0)


@dataclass
class Env:
    altitude_m: float = 0.0
    temp_c: float = 22.0
    humidity_pct: float = 50.0
    pressure_hpa: float = 1013.25


@dataclass
class Signals:
    hr_bpm: float = 70.0
    hrv_rmssd: Optional[float] = None
    spo2: Optional[float] = None
    sleep_score: Optional[float] = None
    accel_load: Optional[float] = None
    sto2: Optional[float] = None
    hhb_dt: Optional[float] = None


def select_tier(s: Signals) -> str:
    tier = "tier1"
    if s.hrv_rmssd is not None:
        tier = "tier2"
    if tier == "tier2" and (s.sto2 is not None or s.hhb_dt is not None):
        tier = "tier3"
    return tier


def compute_index(s: Signals, env: Optional[Env] = None) -> float:
    env = env or Env()
    hr_n = clamp(1.0 - ((s.hr_bpm - 50.0) / 80.0), 0.0, 1.0)

    hrv_n = linear_norm(s.hrv_rmssd, 10.0, 120.0) if s.hrv_rmssd is not None else None
    spo2_n = linear_norm(s.spo2, 90.0, 100.0) if s.spo2 is not None else None
    sleep_n = linear_norm(s.sleep_score, 0.0, 100.0) if s.sleep_score is not None else None

    load_n = None
    if s.accel_load is not None:
        x = s.accel_load
        if x > 1.0:
            x = linear_norm(x, 0.0, 10.0)
        load_n = clamp(1.0 - x, 0.0, 1.0)

    sto2_n = None
    if s.sto2 is not None:
        x = s.sto2 / 100.0 if s.sto2 > 1.0 else s.sto2
        sto2_n = clamp(x, 0.0, 1.0)

    hhb_n = None
    if s.hhb_dt is not None:
        hhb_n = clamp(1.0 - ((s.hhb_dt + 0.02) / 0.04), 0.0, 1.0)

    tier = select_tier(s)

    parts: List[float] = []
    wsum = 0.0

    def add(w: float, v: Optional[float]):
        nonlocal wsum
        if v is None:
            return
        parts.append(w * v)
        wsum += w

    if tier == "tier1":
        add(0.35, hr_n); add(0.25, spo2_n); add(0.20, sleep_n); add(0.20, load_n)
    elif tier == "tier2":
        add(0.25, hr_n); add(0.30, hrv_n); add(0.20, spo2_n); add(0.15, sleep_n); add(0.10, load_n)
    elif tier == "tier3":
        add(0.20, hr_n); add(0.25, hrv_n); add(0.15, spo2_n); add(0.10, sleep_n)
        add(0.10, load_n); add(0.10, sto2_n); add(0.10, hhb_n)

    fused = sum(parts) / (wsum if wsum > 0 else 1.0)

    # Env factor
    alt = max(0.0, env.altitude_m)
    temp_dev = abs(env.temp_c - 22.0)
    hum_dev = abs(env.humidity_pct - 50.0)
    pres_dev = abs(env.pressure_hpa - 1013.25)
    penalty = 0.012 * (alt / 1000) + 0.008 * temp_dev + 0.005 * (hum_dev / 10) + 0.002 * (pres_dev / 10)
    c_env = clamp(1.0 / (1.0 + penalty), 0.85, 1.15)

    return clamp(fused * c_env, 0.0, 1.0)


# ── Anomaly Detection (from .docx section 5) ────────────────────────

def anomaly_score(index: float, slope: float, hr_bpm: float) -> Tuple[int, bool, str]:
    score = 0
    if hr_bpm > 120:
        score += 25
    if index < 0.35:
        score += 35
    if slope < -1e-6:
        score += 20
    coercion = score >= 60
    reason = "coercion_suspected" if coercion else "ok"
    return clamp(score, 0, 100), coercion, reason


# ── Sliding Window & Dynamic ID ──────────────────────────────────────

@dataclass
class IndexPoint:
    ts: int
    index: float


class SlidingWindow:
    def __init__(self, window_days: int = 60):
        self.window_days = window_days
        self.points: List[IndexPoint] = []

    def add(self, p: IndexPoint):
        self.points.append(p)
        max_len = max(5, self.window_days + 5)
        if len(self.points) > max_len:
            self.points = self.points[-max_len:]

    def vector(self) -> Dict[str, float]:
        if not self.points:
            return {"index": 0.0, "slope": 0.0, "mean": 0.0, "std": 0.0}

        xs = [p.index for p in self.points]
        ts = [p.ts for p in self.points]
        mean = sum(xs) / len(xs)
        std = (sum((x - mean) ** 2 for x in xs) / max(len(xs) - 1, 1)) ** 0.5

        slope = 0.0
        if len(xs) > 1:
            t0 = ts[0]
            tt = [float(t - t0) for t in ts]
            tmean = sum(tt) / len(tt)
            num = sum((tt[i] - tmean) * (xs[i] - mean) for i in range(len(xs)))
            den = sum((tt[i] - tmean) ** 2 for i in range(len(xs))) or 1.0
            slope = num / den

        return {"index": xs[-1], "slope": slope, "mean": mean, "std": std}


def generate_dynamic_id(vector: Dict[str, float], secret: str = "local_secret") -> str:
    payload = json.dumps(vector, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hmac.new(secret.encode(), payload, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")


# ── Client ───────────────────────────────────────────────────────────

class MitoPulseClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url

    def post_event(self, **kwargs) -> dict:
        r = requests.post(f"{self.base_url}/v1/identity-events", json=kwargs, timeout=10)
        r.raise_for_status()
        return r.json()

    def verify(self, **kwargs) -> dict:
        r = requests.post(f"{self.base_url}/v1/verify", json=kwargs, timeout=10)
        r.raise_for_status()
        return r.json()


# ── Main Simulation ──────────────────────────────────────────────────

def main():
    client = MitoPulseClient()
    window = SlidingWindow(60)
    env = Env(altitude_m=550, temp_c=22, humidity_pct=45, pressure_hpa=1013)

    user_id = "enterprise_user"
    device_id = "galaxy_watch_sim"

    # Simulate 5 "days" of watch data
    scenarios = [
        # Day 1: Normal resting state (Tier 2)
        {"hr": 68, "hrv": 55, "spo2": 97, "sleep": 82, "load": 0.3, "label": "Normal Resting"},
        # Day 2: Post-exercise (Tier 2)
        {"hr": 85, "hrv": 35, "spo2": 96, "sleep": 70, "load": 0.7, "label": "Post-Exercise"},
        # Day 3: Well-rested (Tier 2)
        {"hr": 62, "hrv": 72, "spo2": 98, "sleep": 90, "load": 0.2, "label": "Well Rested"},
        # Day 4: Stressed (Tier 2)
        {"hr": 95, "hrv": 18, "spo2": 95, "sleep": 45, "load": 0.5, "label": "Stressed"},
        # Day 5: COERCION scenario (Tier 2, high HR + low everything)
        {"hr": 135, "hrv": 12, "spo2": 93, "sleep": 20, "load": 0.9, "label": "⚠ COERCION TEST"},
    ]

    print("\n" + "=" * 70)
    print("  MitoPulse Program Final – Full Enterprise Simulation")
    print("  Watch → Phone Engine → Backend → Dashboard")
    print("=" * 70)

    base_ts = int(time.time()) - 86400 * len(scenarios)
    last_dyn = None
    last_ts = None

    for i, sc in enumerate(scenarios):
        ts = base_ts + 86400 * i
        signals = Signals(
            hr_bpm=sc["hr"],
            hrv_rmssd=sc.get("hrv"),
            spo2=sc.get("spo2"),
            sleep_score=sc.get("sleep"),
            accel_load=sc.get("load"),
        )
        tier = select_tier(signals)
        idx = compute_index(signals, env)
        window.add(IndexPoint(ts, idx))
        vec = window.vector()
        slope = vec["slope"]
        dyn = generate_dynamic_id(vec)

        risk, coercion, anomaly_reason = anomaly_score(idx, slope, signals.hr_bpm)

        request_id = str(uuid4())
        event_id = str(uuid4())

        print(f"\n── Day {i+1}: {sc['label']} {'─' * (40 - len(sc['label']))}")
        print(f"   HR={sc['hr']}  HRV={sc.get('hrv','-')}  SpO2={sc.get('spo2','-')}  Sleep={sc.get('sleep','-')}")
        print(f"   Index={idx:.3f}  Slope={slope:.6f}  Tier={tier}")
        print(f"   Risk={risk}  Coercion={coercion}  ({anomaly_reason})")
        print(f"   DynamicID={dyn[:20]}…")

        res = client.post_event(
            event_id=event_id,
            request_id=request_id,
            user_id=user_id,
            device_id=device_id,
            ts=ts,
            dynamic_id=dyn,
            mitopulse_index=idx,
            slope=slope,
            tier=tier,
            risk_score=risk,
            flag_coercion_suspected=coercion,
        )
        print(f"   Backend: {res}")

        last_dyn = dyn
        last_ts = ts

    # ── Verification ──
    print("\n" + "=" * 70)
    print("  Verification Tests")
    print("=" * 70)

    # Test 1: Valid verification
    rid1 = str(uuid4())
    v1 = client.verify(
        request_id=rid1,
        user_id=user_id,
        device_id=device_id,
        ts=last_ts,
        dynamic_id=last_dyn,
    )
    print(f"\n✅ Valid Verify:   {v1}")

    # Test 2: Anti-replay (same request_id)
    v2 = client.verify(
        request_id=rid1,
        user_id=user_id,
        device_id=device_id,
        ts=last_ts,
        dynamic_id=last_dyn,
    )
    print(f"🔒 Replay Block:  {v2}")

    # Test 3: Mismatch (wrong dynamic_id)
    rid3 = str(uuid4())
    v3 = client.verify(
        request_id=rid3,
        user_id=user_id,
        device_id=device_id,
        ts=last_ts,
        dynamic_id="TAMPERED_FAKE_ID",
    )
    print(f"❌ Tamper Detect:  {v3}")

    print("\n" + "=" * 70)
    print("  ✅ Simulation Complete!")
    print(f"  Dashboard: http://127.0.0.1:8000/dashboard")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
