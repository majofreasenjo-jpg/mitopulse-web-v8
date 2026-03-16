
import argparse, requests, uuid, time, random
from mitopulse_edge.keystore import load_or_create
from mitopulse_edge.engine import EdgeNode, Signals, Env

def post(base, packet):
    r = requests.post(base + "/v2/identity-events", json=packet, timeout=10)
    return r.status_code, r.json() if r.headers.get("content-type","").startswith("application/json") else r.text

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    ap.add_argument("--tenant", default="demo")
    ap.add_argument("--user", default="manuel")
    ap.add_argument("--device", default="note9")
    ap.add_argument("--epoch", type=int, default=1)
    args = ap.parse_args()

    priv = load_or_create(args.device)
    node = EdgeNode(args.tenant, args.user, args.device, args.epoch, priv)

    # 5 scenarios including Tier0 fallback and coercion
    scenarios = [
        ("normal", Signals(hr=62, hrv_rmssd=42, spo2=0.97, sleep_score=0.70, load=2.0), Env(temp_c=22, humidity_pct=50, pressure_hpa=1013)),
        ("post_exercise", Signals(hr=96, hrv_rmssd=28, spo2=0.96, sleep_score=0.55, load=7.0), Env(temp_c=24, humidity_pct=55, pressure_hpa=1010)),
        ("well_rested", Signals(hr=58, hrv_rmssd=55, spo2=0.98, sleep_score=0.85, load=1.5), Env(temp_c=21, humidity_pct=45, pressure_hpa=1014)),
        ("phone_basic_tier0", Signals(hr=74, tap_rate=18, keystroke_var=0.32, sleep_score=0.62, load=3.0), Env(temp_c=23, humidity_pct=52)),
        ("coercion", Signals(hr=118, hrv_rmssd=16, spo2=0.91, sleep_score=0.30, load=9.0), Env(temp_c=30, humidity_pct=70, pressure_hpa=1005)),
    ]

    ts0 = int(time.time())
    for i,(name,sig,env) in enumerate(scenarios, start=1):
        rid = str(uuid.uuid4())
        pkt = node.build_packet(sig, env, request_id=rid, ts=ts0 + i*5)
        code, out = post(args.base, pkt)
        print(f"{i} {name} ->", code, out)

if __name__ == "__main__":
    main()
