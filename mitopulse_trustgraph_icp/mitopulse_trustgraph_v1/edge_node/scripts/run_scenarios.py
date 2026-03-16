from __future__ import annotations

import argparse
import json
import os
import time
import uuid

from mitopulse_edge.engine import (
    Signals,
    Env,
    RollingWindow,
    build_proof_packet,
    build_icp_start_payload,
    build_icp_complete_payload,
    hmac_sha256_b64,
)
from mitopulse_edge.client import MitoPulseGatewayClient


def load_env(path: str) -> dict:
    out = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=None)
    ap.add_argument("--env", default=".demo_env")
    args = ap.parse_args()

    env = load_env(args.env)
    base = args.base or env["BASE"]
    tenant = env["TENANT"]
    api_key = env["API_KEY"]

    # secrets
    secret_note9 = env["SECRET_MANUEL_NOTE9"]
    secret_watch = env["SECRET_MANUEL_WATCH_R800"]
    secret_basic = env["SECRET_ALICE_PHONE_BASIC"]

    client = MitoPulseGatewayClient(base, tenant, api_key)

    w_note9 = RollingWindow(60)
    w_watch = RollingWindow(60)
    w_basic = RollingWindow(30)

    print("== Scenario A: Tier1 phone signals (note9) ==")
    for i, sig in enumerate([
        Signals(hr=78, spo2=97, sleep_score=72, load=0.35),
        Signals(hr=88, spo2=96, sleep_score=60, load=0.55),
        Signals(hr=92, spo2=95, sleep_score=55, load=0.65),
    ]):
        pkt = build_proof_packet(
            tenant_id=tenant,
            user_id="manuel",
            device_id="note9",
            epoch=1,
            secret_b64=secret_note9,
            window=w_note9,
            signals=sig,
            env=Env(altitude_m=520, temp_c=26, humidity=55, pressure_hpa=1009),
            context_fp="work:morning",
        )
        res = client.post_packet(pkt)
        print(i+1, res)
        time.sleep(0.2)

    print("\n== Scenario B: Tier2 wearable signals (watch-r800) + coercion day ==")
    for i, sig in enumerate([
        Signals(hr=72, hrv_rmssd=42, spo2=97, sleep_score=78, load=0.25),
        Signals(hr=74, hrv_rmssd=40, spo2=97, sleep_score=75, load=0.30),
        # coercion-like
        Signals(hr=108, hrv_rmssd=12, spo2=93, sleep_score=40, load=0.85),
    ]):
        pkt = build_proof_packet(
            tenant_id=tenant,
            user_id="manuel",
            device_id="watch-r800",
            epoch=1,
            secret_b64=secret_watch,
            window=w_watch,
            signals=sig,
            env=Env(altitude_m=520, temp_c=26, humidity=55, pressure_hpa=1009),
            context_fp="work:morning",
        )
        res = client.post_packet(pkt)
        print(i+1, res)
        time.sleep(0.2)

    print("\n== Scenario C: Tier0 (celular básico / sin sensores) + check-ins ==")
    for i in range(3):
        pkt = build_proof_packet(
            tenant_id=tenant,
            user_id="alice",
            device_id="phone-basic",
            epoch=1,
            secret_b64=secret_basic,
            window=w_basic,
            signals=Signals(),
            env=Env(altitude_m=520, temp_c=26, humidity=55, pressure_hpa=1009),
            context_fp="work:morning",
        )
        res = client.post_packet(pkt)
        print(i+1, res)
        time.sleep(0.2)

    print("\n== Scenario D: ICP migration (note9 -> watch-r800) ==")
    # Start handoff: old device signs a start payload
    start_payload = build_icp_start_payload(tenant, "manuel", "note9", "watch-r800")
    start_sig = hmac_sha256_b64(secret_note9, json.dumps(start_payload, separators=(",", ":")).encode("utf-8"))
    start_body = {
        "tenant_id": tenant,
        "user_id": "manuel",
        "old_device_id": "note9",
        "new_device_id": "watch-r800",
        "request_id": str(uuid.uuid4()),
        "ts": int(time.time()),
        "payload": start_payload,
        "sig": start_sig,
    }
    r1 = client.icp_start(start_body)
    print("icp_start", r1)
    token = r1["json"].get("handoff_token")

    # Complete handoff: new device signs completion payload
    comp_payload = build_icp_complete_payload(tenant, "manuel", "watch-r800", token)
    comp_sig = hmac_sha256_b64(secret_watch, json.dumps(comp_payload, separators=(",", ":")).encode("utf-8"))
    comp_body = {
        "tenant_id": tenant,
        "user_id": "manuel",
        "new_device_id": "watch-r800",
        "handoff_token": token,
        "request_id": str(uuid.uuid4()),
        "ts": int(time.time()),
        "payload": comp_payload,
        "sig": comp_sig,
    }
    r2 = client.icp_complete(comp_body)
    print("icp_complete", r2)

    print("\nHecho. Abre el dashboard: /dashboard?tenant_id=demo")


if __name__ == "__main__":
    main()
