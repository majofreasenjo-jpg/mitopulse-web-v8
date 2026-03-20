"""MitoPulse v3 Simulator (Ed25519 + ICP + Quorum + Recovery)"""
import argparse, base64, json, time, random, requests
from nacl.signing import SigningKey

def b64(b: bytes) -> str:
    return base64.b64encode(b).decode("utf-8")

def sign_json(sk: SigningKey, payload: dict) -> dict:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")
    payload["signature_b64"] = b64(sk.sign(raw).signature)
    return payload

def post(base, path, obj):
    r = requests.post(base + path, json=obj, timeout=15)
    return r.status_code, r.json()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    ap.add_argument("--tenant", default="demo")
    args = ap.parse_args()
    base = args.base.rstrip("/")
    tenant = args.tenant

    users = {"manuel":["note9","watch_r800"], "sofia":["iphone14"]}
    keys = {}
    for u, devs in users.items():
        for d in devs:
            sk = SigningKey.generate()
            keys[(u,d)] = sk
            post(base, "/v3/device/register", {"tenant_id":tenant,"user_id":u,"device_id":d,"pubkey_b64":b64(bytes(sk.verify_key))})

    group_id = "team-alpha"
    for u in ["manuel","sofia"]:
        post(base, "/v3/group/membership", {"tenant_id":tenant,"group_id":group_id,"user_id":u,"role":"member"})

    def send_event(user, device, epoch, tier, idx=None, human=None, coercion=False, risk=None, stability=None):
        sk = keys[(user,device)]
        ts = int(time.time())
        idx = float(idx if idx is not None else round(random.uniform(0.25, 0.78), 3))
        human = float(human if human is not None else round(random.uniform(0.75, 0.92), 2))
        payload = {
            "tenant_id":tenant,"user_id":user,"device_id":device,"epoch":epoch,"ts":ts,"tier":tier,
            "idx":idx,
            "stability": float(stability if stability is not None else round(random.uniform(0.45, 0.88), 3)),
            "human":human,
            "risk": int(risk if risk is not None else random.uniform(20,65)),
            "coercion": bool(coercion),
            "meta": {"demo":"v3"}
        }
        post(base, "/v3/identity/event", sign_json(sk, payload))

    for _ in range(6):
        send_event("manuel","note9",1,"tier2")
        send_event("sofia","iphone14",1,"tier2")
        time.sleep(0.35)

    # Coercion-like
    send_event("manuel","note9",1,"tier2", idx=0.12, human=0.69, coercion=True, risk=95, stability=0.42)

    # ICP handoff (note9 -> watch_r800, epoch 2)
    token = json.dumps({"tenant_id":tenant,"user_id":"manuel","old_device":"note9","new_device":"watch_r800","ts":int(time.time())},
                       separators=(",",":")).encode("utf-8")
    token_sig = keys[("manuel","note9")].sign(token).signature
    post(base, "/v3/icp/handoff", {
        "tenant_id":tenant,"user_id":"manuel","old_device_id":"note9","new_device_id":"watch_r800",
        "old_epoch":1,"new_epoch":2,"handoff_token_b64":b64(token),"handoff_sig_b64":b64(token_sig)
    })
    for _ in range(3):
        send_event("manuel","watch_r800",2,"tier2", idx=0.62, human=0.87, risk=35, stability=0.71)
        time.sleep(0.25)
    post(base, "/v3/icp/complete", {"tenant_id":tenant,"user_id":"manuel","old_device_id":"note9","new_device_id":"watch_r800","old_epoch":1,"new_epoch":2,"min_events_new":2})

    # Quorum verify (should fail because manuel is risky)
    post(base, "/v3/verify/group", {"tenant_id":tenant,"group_id":group_id,"action":"approve_sensitive_transfer",
        "accepted":["sofia","manuel"],"policy":{"require_quorum":2,"min_stability":0.55,"max_risk":60}})

    # Recovery without old device -> new device pc_basic, epoch 3, tier0
    sk_pc = SigningKey.generate()
    keys[("manuel","pc_basic")] = sk_pc
    st, rr = post(base, "/v3/recovery/request", {"tenant_id":tenant,"user_id":"manuel","lost_device_id":"watch_r800","new_device_id":"pc_basic",
        "new_pubkey_b64":b64(bytes(sk_pc.verify_key)),"group_id":group_id,"require_quorum":2})
    req_id = rr.get("request_id")
    post(base, "/v3/recovery/approve", {"tenant_id":tenant,"group_id":group_id,"approver_user_id":"sofia","target_user_id":"manuel","request_id":req_id})
    post(base, "/v3/recovery/approve", {"tenant_id":tenant,"group_id":group_id,"approver_user_id":"manuel","target_user_id":"manuel","request_id":req_id})
    post(base, "/v3/recovery/complete", {"tenant_id":tenant,"request_id":req_id})

    send_event("manuel","pc_basic",3,"tier0", idx=0.58, human=0.80, risk=55, stability=0.63)

    print("✅ Simulation complete.")
    print("Dashboard:", base + "/dashboard")

if __name__ == "__main__":
    main()
