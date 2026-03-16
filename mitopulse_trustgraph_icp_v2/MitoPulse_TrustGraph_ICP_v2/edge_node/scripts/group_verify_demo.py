
import argparse, requests, uuid, time
from mitopulse_edge.keystore import load_or_create
from mitopulse_edge.engine import EdgeNode, Signals, Env

def reg(base, tenant, user, device, pub):
    return requests.post(base + "/v2/device/register", json={"tenant_id":tenant,"user_id":user,"device_id":device,"pubkey_b64":pub}, timeout=10)

def membership(base, tenant, group_id, user):
    return requests.post(base + "/v2/group/membership", json={"tenant_id":tenant,"group_id":group_id,"user_id":user,"role":"member"}, timeout=10)

def post_event(base, packet):
    return requests.post(base + "/v2/identity-events", json=packet, timeout=10)

def verify(base, tenant_id, user_id, device_id, epoch, ts, request_id, packet_hash):
    return {"tenant_id":tenant_id,"user_id":user_id,"device_id":device_id,"epoch":epoch,"ts":ts,"request_id":request_id,"packet_hash":packet_hash}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    ap.add_argument("--tenant", default="demo")
    ap.add_argument("--group", default="team-alpha")
    args = ap.parse_args()

    # Two members
    members=[("manuel","note9"),("sofia","iphone14")]
    nodes=[]
    ts=int(time.time())

    for user,dev in members:
        priv=load_or_create(dev)
        node=EdgeNode(args.tenant,user,dev,1,priv)
        reg(args.base,args.tenant,user,dev,node.pubkey_b64())
        membership(args.base,args.tenant,args.group,user)
        pkt=node.build_packet(Signals(hr=64, hrv_rmssd=40, spo2=0.97, sleep_score=0.72, load=2.0), Env(temp_c=22, humidity_pct=50, pressure_hpa=1013), request_id=str(uuid.uuid4()), ts=ts)
        r=post_event(args.base,pkt)
        j=r.json()
        nodes.append(verify(args.base,args.tenant,user,dev,1,ts,pkt["request_id"],j["packet_hash"]))

    gv = requests.post(args.base + "/v2/verify/group", json={"tenant_id":args.tenant,"group_id":args.group,"action":"approve_sensitive_transfer","proofs":nodes}, timeout=10)
    print("group verify:", gv.status_code, gv.text)

if __name__ == "__main__":
    main()
