
import argparse, requests, uuid, time
from mitopulse_edge.keystore import load_or_create
from mitopulse_edge.engine import EdgeNode, Signals, Env

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    ap.add_argument("--tenant", default="demo")
    ap.add_argument("--user", default="manuel")
    ap.add_argument("--old", default="note9")
    ap.add_argument("--new", default="watch_r800")
    args = ap.parse_args()

    ts=int(time.time())

    # old device handoff
    old_priv=load_or_create(args.old)
    old_node=EdgeNode(args.tenant,args.user,args.old,1,old_priv)
    # register old/new
    requests.post(args.base + "/v2/device/register", json={"tenant_id":args.tenant,"user_id":args.user,"device_id":args.old,"pubkey_b64":old_node.pubkey_b64()}, timeout=10)

    pkt = old_node.build_packet(Signals(hr=62, hrv_rmssd=42, spo2=0.97, sleep_score=0.70, load=2.0),
                                Env(temp_c=22, humidity_pct=50, pressure_hpa=1013),
                                request_id=str(uuid.uuid4()), ts=ts)
    r = requests.post(args.base + "/v2/icp/handoff", json=pkt, timeout=10)
    print("handoff:", r.status_code, r.text)
    handoff_hash = r.json().get("handoff_hash")

    new_priv=load_or_create(args.new)
    new_node=EdgeNode(args.tenant,args.user,args.new,2,new_priv)
    requests.post(args.base + "/v2/device/register", json={"tenant_id":args.tenant,"user_id":args.user,"device_id":args.new,"pubkey_b64":new_node.pubkey_b64()}, timeout=10)

    c = requests.post(args.base + "/v2/icp/complete", params={
        "tenant_id": args.tenant,
        "user_id": args.user,
        "old_device_id": args.old,
        "old_epoch": 1,
        "new_device_id": args.new,
        "new_epoch": 2,
        "handoff_hash": handoff_hash
    }, timeout=10)
    print("complete:", c.status_code, c.text)

if __name__ == "__main__":
    main()
