
import argparse, requests, uuid
from mitopulse_edge.keystore import load_or_create
from mitopulse_edge.engine import EdgeNode

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
    pub = node.pubkey_b64()

    r = requests.post(args.base + "/v2/device/register", json={
        "tenant_id": args.tenant,
        "user_id": args.user,
        "device_id": args.device,
        "pubkey_b64": pub
    }, timeout=10)
    print("register:", r.status_code, r.text)

if __name__ == "__main__":
    main()
