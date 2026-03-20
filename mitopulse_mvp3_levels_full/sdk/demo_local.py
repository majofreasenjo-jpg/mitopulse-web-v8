"""End-to-end demo:

1) Reads sdk/sample.csv (3 rows)
2) Computes MitoPulse index + slope + dynamic_id locally (SDK)
3) Posts derived identity events to backend
4) Calls /v1/verify (on-demand) for the last dynamic_id

Run:
  # Terminal 1
  cd backend && python -m venv .venv
  source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
  pip install -r requirements.txt
  python -m uvicorn main:app --reload

  # Terminal 2
  cd sdk && python -m venv .venv
  source .venv/bin/activate
  pip install -e .
  python demo_local.py

Then open:
  http://127.0.0.1:8000/dashboard
  http://127.0.0.1:8000/docs
"""

from __future__ import annotations

import csv
import os
from datetime import datetime, timezone
from uuid import uuid4

from mitopulse_sdk import Sample, Env, LocalIdentityEngine
from mitopulse_sdk.client import MitoPulseClient


def iso_to_ts(iso: str) -> int:
    if len(iso) == 10:
        dt = datetime.fromisoformat(iso).replace(tzinfo=timezone.utc)
    else:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(timezone.utc)
    return int(dt.timestamp())


def read_samples(csv_path: str) -> list[Sample]:
    out: list[Sample] = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            out.append(
                Sample(
                    ts=iso_to_ts(row["timestamp"]),
                    hr=float(row.get("hr") or 0),
                    hrv_rmssd=float(row.get("hrv_rmssd") or 0),
                    spo2=float(row.get("spo2") or 0),
                    sleep_score=float(row.get("sleep_score") or 0),
                    accel_load=float(row.get("accel_load") or 0),
                )
            )
    return out


def main() -> None:
    here = os.path.dirname(__file__)
    csv_path = os.path.join(here, "sample.csv")

    user_id = "demo_user"
    device_id = "demo_device"
    secret = "demo_secret_local_only"  # in real device: keep in secure enclave/keystore

    env = Env(altitude_m=550, temp_c=22, humidity_pct=45, pressure_hpa=1013)
    samples = read_samples(csv_path)

    engine = LocalIdentityEngine(secret=secret, window_days=60)
    client = MitoPulseClient(base_url="http://127.0.0.1:8000")

    print("\n== Local computation + post identity events ==")
    last = None
    for s in samples:
        s.env = env
        result = engine.process(s)
        last = result

        print(
            f"ts={s.ts}  idx={result['mitopulse_index']:.3f}  slope={result['slope']:.3f}  dyn={result['dynamic_id'][:12]}..."
        )

        client.post_identity_event(
            user_id=user_id,
            device_id=device_id,
            ts=s.ts,
            dynamic_id=result["dynamic_id"],
            mitopulse_index=result["mitopulse_index"],
            slope=result["slope"],
            tier=result["tier"],
            event_id=str(uuid4()),
        )

    assert last is not None

    print("\n== Verify (on-demand) ==")
    verify_1 = client.verify(
        user_id=user_id,
        device_id=device_id,
        dynamic_id=last["dynamic_id"],
        ts=samples[-1].ts,
    )
    print(verify_1)

    print("\n== Verify replay check (same request_id must fail) ==")
    rid = str(uuid4())
    ok1 = client.verify(user_id=user_id, device_id=device_id, dynamic_id=last["dynamic_id"], ts=samples[-1].ts, request_id=rid)
    ok2 = client.verify(user_id=user_id, device_id=device_id, dynamic_id=last["dynamic_id"], ts=samples[-1].ts, request_id=rid)
    print("first:", ok1)
    print("second:", ok2)


if __name__ == "__main__":
    main()
