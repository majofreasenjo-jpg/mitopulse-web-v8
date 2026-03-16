
import argparse, time, uuid, requests
from engine_v25 import Signals, Env, compute_index, compute_risk, dynamic_id_hmac, sign_payload, human_confidence

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="http://127.0.0.1:8000")
    ap.add_argument("--user", default="manuel")
    ap.add_argument("--device", default="sim-device-01")
    ap.add_argument("--api_key", default="")
    args = ap.parse_args()

    headers = {}
    if args.api_key:
        headers["X-API-Key"] = args.api_key

    secret = b"demo-super-secret-device-key"

    scenarios = [
        ("Normal Resting", 72, 45, 98, 80, 1.0),
        ("Post Exercise", 110, 28, 97, 65, 6.5),
        ("Well Rested", 65, 55, 99, 90, 1.2),
        ("Stressed", 95, 22, 96, 60, 3.0),
        ("Coercion Test", 135, 15, 91, 45, 2.0),
    ]

    prev = None
    print("== v2.5 demo ==")
    for i, sc in enumerate(scenarios, start=1):
        name, hr, hrv, spo2, sleep, load = sc
        ts = int(time.time()) + i
        sig = Signals(hr=hr, hrv_rmssd=hrv, spo2=spo2, sleep_score=sleep, load=load)
        env = Env(altitude_m=120, temp_c=22, humidity_pct=45, pressure_hpa=1012)

        idx, tier, _ = compute_index(sig, env)
        risk, coercion = compute_risk(sig, idx)
        hc = human_confidence(sig, idx, prev)

        dyn = dynamic_id_hmac(secret, {"index": idx, "tier": tier, "risk": risk, "ts": ts})

        payload = {
            "user_id": args.user,
            "device_id": args.device,
            "ts": ts,
            "request_id": str(uuid.uuid4()),
            "tier": tier,
            "index_value": idx,
            "slope": 0.0,
            "risk": risk,
            "coercion": coercion,
            "dynamic_id": dyn,
            "human_confidence": hc,
            "hr": hr, "hrv_rmssd": hrv, "spo2": spo2, "sleep_score": sleep, "load": load,
            "altitude_m": env.altitude_m, "temp_c": env.temp_c, "humidity_pct": env.humidity_pct, "pressure_hpa": env.pressure_hpa,
        }
        payload["signature"] = sign_payload(secret, {k:v for k,v in payload.items() if k != "signature"})

        r = requests.post(args.backend + "/v1/identity-events", json=payload, headers=headers, timeout=20)
        print(f"DAY {i} {name:14s} -> {r.status_code} idx={idx:.3f} tier={tier} risk={risk} coercion={coercion} human={hc:.2f}")
        prev = {"index": idx}

    verify_payload = {"user_id": args.user, "device_id": args.device, "dynamic_id": dyn, "request_id": str(uuid.uuid4())}
    vr = requests.post(args.backend + "/v1/verify", json=verify_payload, headers=headers, timeout=20)
    print("VERIFY:", vr.status_code, vr.text)

    st = requests.get(args.backend + f"/v2/identity/state?user_id={args.user}&device_id={args.device}", headers=headers, timeout=20)
    print("STATE:", st.status_code, st.text)

    hp = requests.get(args.backend + f"/v2/identity/human-proof?user_id={args.user}&device_id={args.device}", headers=headers, timeout=20)
    print("HUMAN-PROOF:", hp.status_code, hp.text)

if __name__ == "__main__":
    main()
