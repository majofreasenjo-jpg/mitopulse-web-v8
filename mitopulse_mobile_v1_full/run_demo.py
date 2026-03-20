import sys, os, time, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import requests
from sdk_shared.engine import Sample, mitopulse_index, vectorize, dynamic_id, risk_score

BACKEND = "http://127.0.0.1:8000"
USER = "enterprise_user_full"
DEVICE = "note9_simulator"
SECRET = b"dev_secret_change_me"

now = int(time.time())
samples = [
    Sample(ts=now-4*86400, hr=72, hrv_rmssd=45, spo2=97, sleep_score=78, accel_load=3.0, altitude_m=500, temp_c=22, humidity=45),
    Sample(ts=now-3*86400, hr=95, hrv_rmssd=35, spo2=96, sleep_score=72, accel_load=6.5, altitude_m=500, temp_c=24, humidity=55),
    Sample(ts=now-2*86400, hr=62, hrv_rmssd=60, spo2=98, sleep_score=90, accel_load=2.0, altitude_m=500, temp_c=22, humidity=45),
    Sample(ts=now-1*86400, hr=105, hrv_rmssd=25, spo2=95, sleep_score=65, accel_load=7.0, altitude_m=500, temp_c=26, humidity=60),
    Sample(ts=now, hr=130, hrv_rmssd=15, spo2=93, sleep_score=55, accel_load=8.0, altitude_m=500, temp_c=28, humidity=70),
]

hist = []
last_dyn = None
for s in samples:
    idx, tier = mitopulse_index(s)
    hist.append(idx)
    vec = vectorize(hist[-60:])
    last_dyn = dynamic_id(SECRET, vec)
    risk, coercion = risk_score(s, idx, vec["slope"])
    evt = dict(
        user_id=USER, device_id=DEVICE, ts=s.ts, request_id=str(uuid.uuid4()),
        dynamic_id=last_dyn, index_value=idx, slope=vec["slope"], tier=tier,
        risk=risk, coercion=coercion, meta={"source": "simulator_full"}
    )
    ts_str = evt["ts"]
    print(f"POST ts={ts_str}  idx={idx:.3f}  tier={tier}  risk={risk}  coercion={coercion}")
    r = requests.post(f"{BACKEND}/v1/identity-events", json=evt, timeout=10)
    print(f"  -> {r.status_code} {r.text}")

# Verify
vr = dict(user_id=USER, device_id=DEVICE, ts=int(time.time()), request_id=str(uuid.uuid4()), dynamic_id=last_dyn)
r = requests.post(f"{BACKEND}/v1/verify", json=vr, timeout=10)
print(f"\nVERIFY: {r.status_code} {r.text}")

# Anti-replay test
rid = str(uuid.uuid4())
vr1 = dict(user_id=USER, device_id=DEVICE, ts=int(time.time()), request_id=rid, dynamic_id=last_dyn)
r1 = requests.post(f"{BACKEND}/v1/verify", json=vr1, timeout=10)
r2 = requests.post(f"{BACKEND}/v1/verify", json=vr1, timeout=10)
print(f"REPLAY TEST 1: {r1.text}")
print(f"REPLAY TEST 2: {r2.text}")
