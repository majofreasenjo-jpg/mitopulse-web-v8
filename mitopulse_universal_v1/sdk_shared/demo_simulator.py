import os, time, uuid, requests, random
from engine import Env, compute_event

BASE_URL = os.getenv("MITOPULSE_BASE_URL", "http://127.0.0.1:8000")
USER = "manuel"
DEVICE = "pc-sim"
SECRET = b"demo_secret_change_me"

def post(evt, request_id):
    payload = {
        "ts": evt["ts"],
        "user_id": evt["user_id"],
        "device_id": evt["device_id"],
        "request_id": request_id,
        "tier_used": evt["tier_used"],
        "index_value": evt["index_value"],
        "slope": evt["slope"],
        "dynamic_id": evt["dynamic_id"],
        "risk": evt["risk"],
        "coercion": evt["coercion"],
        "signature": None,
    }
    r = requests.post(f"{BASE_URL}/v1/identity-events", json=payload, timeout=10)
    return r.status_code, r.text

def verify(request_id, dynamic_id):
    r = requests.post(f"{BASE_URL}/v1/verify", json={
        "user_id": USER, "device_id": DEVICE, "request_id": request_id, "dynamic_id": dynamic_id
    }, timeout=10)
    return r.status_code, r.text

def main():
    env = Env(altitude_m=520, temp_c=22, humidity=50, pressure_hpa=1013)
    history = []
    ts0 = int(time.time()) - 4*86400
    scenarios = [
        {"hr":70, "hrv_rmssd":38, "spo2":97, "sleep_score":78, "accel_load":0.20}, # normal
        {"hr":92, "hrv_rmssd":25, "spo2":96, "sleep_score":65, "accel_load":1.10}, # post exercise
        {"hr":62, "hrv_rmssd":55, "spo2":98, "sleep_score":88, "accel_load":0.10}, # well rested
        {"hr":98, "hrv_rmssd":18, "spo2":95, "sleep_score":55, "accel_load":0.60}, # stressed
        {"hr":115,"hrv_rmssd":10, "spo2":92, "sleep_score":40, "accel_load":0.05}, # coercion test
    ]
    print("== Local computation + post identity events ==")
    last_dyn = None
    for i, sig in enumerate(scenarios):
        ts = ts0 + i*86400
        evt = compute_event(SECRET, ts, USER, DEVICE, sig, env, history)
        history = evt["history"]
        rid = str(uuid.uuid4())
        code, text = post(evt, rid)
        print(f"POST day{i+1} ts={ts} idx={evt['index_value']:.3f} tier={evt['tier_used']} risk={evt['risk']} coercion={evt['coercion']}  -> {code}")
        last_dyn = evt["dynamic_id"]

    print("== Verify (on-demand) ==")
    ridv = str(uuid.uuid4())
    code, text = verify(ridv, last_dyn)
    print(code, text)

    print("== Verify replay check (same request_id must fail) ==")
    ridr = str(uuid.uuid4())
    code1, t1 = verify(ridr, last_dyn)
    code2, t2 = verify(ridr, last_dyn)
    print("first:", code1, t1)
    print("second:", code2, t2)

if __name__ == "__main__":
    main()
