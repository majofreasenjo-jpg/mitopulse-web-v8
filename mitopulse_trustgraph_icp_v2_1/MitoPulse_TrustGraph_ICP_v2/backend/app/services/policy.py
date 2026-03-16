
from __future__ import annotations
from typing import Dict, Any, List, Tuple
import time, json
from ..db.db import fetchone, fetchall

DEFAULT_POLICY = {
  "allowed_skew_seconds": 86400,
  "group_verify": {
    "window_seconds": 600,
    "require_quorum": 2,
    "min_stability_band": 0.55,
    "max_risk": 60
  }
}

def get_policy(conn, tenant_id: str) -> Dict[str,Any]:
    row = fetchone(conn, "SELECT policy_json FROM tenants WHERE tenant_id=?", (tenant_id,))
    if not row:
        return DEFAULT_POLICY
    try:
        return json.loads(row["policy_json"])
    except Exception:
        return DEFAULT_POLICY

def group_members(conn, tenant_id: str, group_id: str) -> List[str]:
    rows = fetchall(conn, "SELECT user_id FROM membership WHERE tenant_id=? AND group_id=?", (tenant_id, group_id))
    return [r["user_id"] for r in rows]

def evaluate_group(conn, tenant_id: str, group_id: str, proofs: List[Dict[str,Any]]) -> Tuple[bool,str,Dict[str,Any]]:
    pol = get_policy(conn, tenant_id)
    gv = pol.get("group_verify", DEFAULT_POLICY["group_verify"])
    window = int(gv.get("window_seconds", 600))
    quorum = int(gv.get("require_quorum", 2))
    min_stab = float(gv.get("min_stability_band", 0.55))
    max_risk = int(gv.get("max_risk", 60))
    members = set(group_members(conn, tenant_id, group_id))
    now = int(time.time())
    accepted=[]
    rejected=[]
    for p in proofs:
        if p["user_id"] not in members:
            rejected.append((p["user_id"],"not_member"))
            continue
        # find latest state for that node
        st = fetchone(conn, "SELECT * FROM identity_state WHERE user_id=? AND device_id=? AND epoch=?", (p["user_id"], p["device_id"], int(p["epoch"])))
        if not st:
            rejected.append((p["user_id"],"no_state"))
            continue
        if abs(int(p["ts"]) - int(st["last_ts"])) > window:
            rejected.append((p["user_id"],"out_of_window"))
            continue
        if float(st["stability_band"]) < min_stab:
            rejected.append((p["user_id"],"low_stability"))
            continue
        # latest event risk for that request_id
        ev = fetchone(conn, "SELECT risk FROM identity_events WHERE request_id=?", (p["request_id"],))
        if not ev:
            rejected.append((p["user_id"],"unknown_request"))
            continue
        if int(ev["risk"]) > max_risk:
            rejected.append((p["user_id"],"risk_too_high"))
            continue
        accepted.append(p["user_id"])
    ok = len(set(accepted)) >= quorum
    meta={"accepted": list(dict.fromkeys(accepted)), "rejected": rejected, "policy": gv}
    return ok, ("ok" if ok else "insufficient_quorum"), meta
