from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict
import json
import hmac
import hashlib
import base64


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
class Sample:
    ts: int
    hr: Optional[float] = None
    hrv_rmssd: Optional[float] = None
    spo2: Optional[float] = None
    sleep_score: Optional[float] = None
    accel_load: Optional[float] = None
    # Tier 3 optional signals (if available from device/API)
    sto2: Optional[float] = None      # tissue oxygenation (0..1 or 0..100)
    hhb_dt: Optional[float] = None    # deoxyhemoglobin derivative


class Engine:
    """Local-first MitoPulse engine (MVP) with 3 computation tiers.

    The engine is designed to be robust to missing signals. It selects the
    highest possible tier for each sample based on signal availability.

    Tier selection:
      - tier1: hr + accel_load (+ optional spo2/sleep)
      - tier2: tier1 + hrv_rmssd
      - tier3: tier2 + (sto2 and/or hhb_dt) when available
    """

    def __init__(
        self,
        window_days: int = 60,
        K: float = 1.0,
        env: Optional[Env] = None,
        secret: Optional[bytes] = None,
    ):
        self.window_days = int(window_days)
        self.K = float(K)
        self.env = env or Env()
        self.secret = secret or b"local_secret_change_me"
        # store (ts, index, tier_used)
        self.series: List[Tuple[int, float, str]] = []

    def _env_factor(self) -> float:
        env = self.env
        alt = max(0.0, float(env.altitude_m))
        temp_dev = abs(float(env.temp_c) - 22.0)
        hum_dev = abs(float(env.humidity_pct) - 50.0)
        pres_dev = abs(float(env.pressure_hpa) - 1013.25)

        penalty = (
            0.012 * (alt / 1000.0)
            + 0.008 * temp_dev
            + 0.005 * (hum_dev / 10.0)
            + 0.002 * (pres_dev / 10.0)
        )
        c_env = 1.0 / (1.0 + penalty)
        return clamp(c_env, 0.85, 1.15)

    def compute_index_and_tier(self, s: Sample) -> Tuple[float, str]:
        # --- Normalize core signals ---
        hr = float(s.hr) if s.hr is not None else 70.0
        # higher HR => lower score
        hr_n = clamp(1.0 - ((hr - 50.0) / 80.0), 0.0, 1.0)

        hrv_n = None
        if s.hrv_rmssd is not None:
            # RMSSD ~ [10..120]ms typical
            hrv_n = linear_norm(float(s.hrv_rmssd), 10.0, 120.0)

        spo2_n = None
        if s.spo2 is not None:
            spo2_n = linear_norm(float(s.spo2), 90.0, 100.0)

        sleep_n = None
        if s.sleep_score is not None:
            sleep_n = linear_norm(float(s.sleep_score), 0.0, 100.0)

        load_n = None
        if s.accel_load is not None:
            # accel_load higher => lower score; accept either [0..1] or small positive [0..10]
            x = float(s.accel_load)
            if x > 1.0:
                x = linear_norm(x, 0.0, 10.0)
            load_n = clamp(1.0 - x, 0.0, 1.0)

        # Tier3 optional signals
        sto2_n = None
        if s.sto2 is not None:
            x = float(s.sto2)
            if x > 1.0:
                x = x / 100.0
            sto2_n = clamp(x, 0.0, 1.0)

        hhb_n = None
        if s.hhb_dt is not None:
            x = float(s.hhb_dt)
            # map [-0.02..0.02] => [1..0]
            hhb_n = clamp(1.0 - ((x + 0.02) / 0.04), 0.0, 1.0)

        # --- Tier selection ---
        tier = "tier1"
        if hrv_n is not None:
            tier = "tier2"
        if tier == "tier2" and (sto2_n is not None or hhb_n is not None):
            tier = "tier3"

        # --- Fusion (renormalized by available signals) ---
        parts: List[float] = []
        wsum = 0.0

        def add(w: float, v: Optional[float]):
            nonlocal wsum
            if v is None:
                return
            parts.append(w * v)
            wsum += w

        # tier1
        add(0.35, hr_n)
        add(0.25, spo2_n)
        add(0.20, sleep_n)
        add(0.20, load_n)

        # tier2: rebalance + HRV
        if tier in ("tier2", "tier3"):
            parts, wsum = [], 0.0
            add(0.25, hr_n)
            add(0.30, hrv_n)
            add(0.20, spo2_n)
            add(0.15, sleep_n)
            add(0.10, load_n)

        # tier3: add NIRS/tissue oxygenation
        if tier == "tier3":
            parts, wsum = [], 0.0
            add(0.20, hr_n)
            add(0.25, hrv_n)
            add(0.15, spo2_n)
            add(0.10, sleep_n)
            add(0.10, load_n)
            add(0.10, sto2_n)
            add(0.10, hhb_n)

        fused = sum(parts) / (wsum if wsum > 0 else 1.0)
        idx = clamp(self.K * fused * self._env_factor(), 0.0, 1.0)
        return float(idx), tier

    def compute_index(self, s: Sample) -> float:
        idx, _ = self.compute_index_and_tier(s)
        return idx

    def update_series(self, ts: int, idx: float, tier: str) -> None:
        self.series.append((int(ts), float(idx), str(tier)))
        # keep last N days (MVP uses 1 sample per day typical)
        max_len = max(5, self.window_days + 5)
        if len(self.series) > max_len:
            self.series = self.series[-max_len:]

    def build_vector(self) -> Dict[str, float | str]:
        if not self.series:
            return {"index": 0.0, "slope": 0.0, "mean": 0.0, "std": 0.0, "tier_used": "tier1"}

        ts = [t for t, _, _ in self.series]
        xs = [i for _, i, _ in self.series]
        tiers = [tr for _, _, tr in self.series]

        mean = sum(xs) / len(xs)
        if len(xs) > 1:
            var = sum((x - mean) ** 2 for x in xs) / (len(xs) - 1)
            std = var ** 0.5
        else:
            std = 0.0

        # slope: simple linear regression over index vs time (normalized by seconds)
        if len(xs) > 1:
            t0 = ts[0]
            tt = [float(t - t0) for t in ts]
            tmean = sum(tt) / len(tt)
            num = sum((tt[i] - tmean) * (xs[i] - mean) for i in range(len(xs)))
            den = sum((tt[i] - tmean) ** 2 for i in range(len(xs))) or 1.0
            slope = num / den
        else:
            slope = 0.0

        # most frequent tier in window
        tier_used = max(set(tiers), key=tiers.count)

        return {
            "index": float(xs[-1]),
            "slope": float(slope),
            "mean": float(mean),
            "std": float(std),
            "tier_used": str(tier_used),
        }

    def dynamic_id(self, vector: Dict[str, float | str]) -> str:
        payload = json.dumps(vector, sort_keys=True, separators=(",", ":")).encode("utf-8")
        digest = hmac.new(self.secret, payload, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(digest)[:12].decode("utf-8")

    def process_sample(self, sample: Sample) -> dict:
        idx, tier = self.compute_index_and_tier(sample)
        self.update_series(sample.ts, idx, tier)
        vector = self.build_vector()
        dyn = self.dynamic_id(vector)
        return {
            "index": idx,
            "env_factor": self._env_factor(),
            "tier_used": tier,
            "vector": vector,
            "dynamic_id": dyn,
        }


class MitoPulseEngine:
    """Compatibility wrapper for earlier MVP versions.

    Earlier code expected:
      - MitoPulseEngine(secret_b64: str)
      - .process(sample: Sample) -> {index, vector, dynamic_id, tier_used, env_factor}
    """

    def __init__(self, secret_b64: str, window_days: int = 60, K: float = 1.0, env: Optional[Env] = None):
        try:
            secret = base64.b64decode(secret_b64.encode("ascii"))
        except Exception:
            secret = secret_b64.encode("utf-8")
        self.window_days = int(window_days)
        self.K = float(K)
        self.env = env or Env()
        self._engine = Engine(window_days=self.window_days, K=self.K, env=self.env, secret=secret)

    def process(self, sample: Sample) -> dict:
        # keep wrapper properties in sync
        self._engine.window_days = int(self.window_days)
        self._engine.K = float(self.K)
        self._engine.env = self.env
        return self._engine.process_sample(sample)
