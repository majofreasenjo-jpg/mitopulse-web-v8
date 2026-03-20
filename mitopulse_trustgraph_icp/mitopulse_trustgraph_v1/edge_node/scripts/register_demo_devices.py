from __future__ import annotations

import argparse
import base64
import os
import time

import requests


def b64_secret(n=32) -> str:
    return base64.b64encode(os.urandom(n)).decode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    args = ap.parse_args()

    base = args.base.rstrip("/")

    # 1) create tenant demo
    tenant_id = "demo"
    r = requests.post(f"{base}/v1/tenants/register", json={"tenant_id": tenant_id, "name": "Demo Tenant"}, timeout=20)
    r.raise_for_status()
    api_key = r.json()["api_key"]

    # 2) register two devices for same user (migration), plus one extra user for cohab cluster
    devices = [
        ("manuel", "note9"),
        ("manuel", "watch-r800"),
        ("alice", "phone-basic"),
    ]
    secrets = {}
    for user_id, device_id in devices:
        secret = b64_secret()
        secrets[(user_id, device_id)] = secret
        rr = requests.post(
            f"{base}/v1/devices/register",
            json={
                "tenant_id": tenant_id,
                "user_id": user_id,
                "device_id": device_id,
                "shared_secret_b64": secret,
                "tier_hint": None,
            },
            headers={"x-api-key": api_key},
            timeout=20,
        )
        rr.raise_for_status()

    print("tenant_id=demo")
    print(f"api_key={api_key}")
    print("\nSECRETS (guardar localmente):")
    for (u, d), s in secrets.items():
        print(f"  {u}/{d}: {s}")

    # Write an env file for scripts
    with open(".demo_env", "w", encoding="utf-8") as f:
        f.write(f"BASE={base}\nTENANT=demo\nAPI_KEY={api_key}\n")
        for (u, d), s in secrets.items():
            f.write(f"SECRET_{u.upper()}_{d.upper().replace('-', '_')}={s}\n")


if __name__ == "__main__":
    main()
