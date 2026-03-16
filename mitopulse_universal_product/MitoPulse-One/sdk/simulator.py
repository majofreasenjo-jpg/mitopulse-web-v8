import argparse, time, json, hmac, hashlib, random, requests

API_KEY = "demo-key"
DEVICE_SECRET = "device-secret-demo"

def hmac_hex(key: str, msg: str) -> str:
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()

def dyn_id(user_id: str, device_id: str, ts: int, index: float, tier: str) -> str:
    payload = json.dumps({"user_id": user_id, "device_id": device_id, "ts": ts, "index": index, "tier": tier}, separators=(",",":"))
    return hmac_hex(DEVICE_SECRET, payload)

def sig(user_id: str, device_id: str, ts: int, dynamic_id: str) -> str:
    return hmac_hex(API_KEY, f"{user_id}|{device_id}|{ts}|{dynamic_id}")

def rand_req() -> str:
    return hashlib.sha256(str(random.random()).encode()).hexdigest()[:32]

def clamp(x,a,b): return max(a, min(b, x))

def compute_index(hr, hrv, spo2, sleep, load, env):
    n_hr = clamp(1 - (hr - 50) / 120, 0, 1)
    n_hrv = clamp((hrv - 10) / 90, 0, 1) if hrv is not None else 0.5
    n_spo2 = clamp((spo2 - 85) / 15, 0, 1) if spo2 is not None else 0.7
    n_sleep = clamp(sleep / 100, 0, 1) if sleep is not None else 0.6
    n_load = clamp(1 - load / 10, 0, 1) if load is not None else 0.6
    F = 0.30*n_hrv + 0.20*n_spo2 + 0.20*n_sleep + 0.15*n_hr + 0.15*n_load
    alt = env.get("altitude_m", 0); temp = env.get("temp_c", 22); hum = env.get("humidity_pct", 50)
    C = 1 / (1 + 0.012*(alt/1000) + 0.008*abs(temp-22) + 0.005*abs(hum-50))
    return clamp(F*C, 0, 1)

def tier_from(hrv, spo2):
    return "tier2" if hrv is not None else ("tier1" if spo2 is not None else "tier1")

def risk_from(signals, idx):
    r = 0
    if signals.get("hrv_rmssd") is not None and signals["hrv_rmssd"] < 18: r += 25
    if signals.get("hr") is not None and signals["hr"] > 120: r += 25
    if signals.get("spo2") is not None and signals["spo2"] < 90: r += 25
    if idx < 0.20: r += 25
    return max(0, min(100, r))

def post_event(backend, user_id, device_id, signals, env):
    ts = int(time.time())
    tier = tier_from(signals.get("hrv_rmssd"), signals.get("spo2"))
    idx = compute_index(signals["hr"], signals.get("hrv_rmssd"), signals.get("spo2"), signals.get("sleep_score"), signals.get("load"), env)
    dynamic_id = dyn_id(user_id, device_id, ts, idx, tier)
    signature = sig(user_id, device_id, ts, dynamic_id)
    risk = risk_from(signals, idx)
    payload = {
        "ts": ts, "user_id": user_id, "device_id": device_id, "request_id": rand_req(),
        "tier": tier, "index": idx, "slope": 0.0, "risk": risk, "coercion": risk >= 60,
        "stability": 1.0, "human_conf": 0.9, "dynamic_id": dynamic_id, "signature": signature,
        "signals": signals, "env": env
    }
    r = requests.post(f"{backend}/identity/event", json=payload, headers={"X-API-Key": API_KEY}, timeout=10)
    return r.status_code, r.json()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="http://127.0.0.1:8000")
    ap.add_argument("--user", default="demo-user")
    ap.add_argument("--device", default="demo-device")
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()

    env = {"altitude_m": 0, "temp_c": 22, "humidity_pct": 50, "pressure_hpa": 1013}

    if args.live:
        while True:
            signals = {"hr": random.randint(60,105), "hrv_rmssd": random.randint(18,60),
                       "spo2": random.randint(92,99), "sleep_score": random.randint(55,92),
                       "load": round(random.random()*6, 1)}
            sc, data = post_event(args.backend, args.user, args.device, signals, env)
            print("POST", sc, data)
            time.sleep(4)
    else:
        for signals in [
            {"hr":72,"hrv_rmssd":42,"spo2":97,"sleep_score":78,"load":3},
            {"hr":92,"hrv_rmssd":28,"spo2":95,"sleep_score":70,"load":6},
            {"hr":128,"hrv_rmssd":14,"spo2":88,"sleep_score":55,"load":8},
        ]:
            sc, data = post_event(args.backend, args.user, args.device, signals, env)
            print("POST", sc, data)

if __name__ == "__main__":
    main()

