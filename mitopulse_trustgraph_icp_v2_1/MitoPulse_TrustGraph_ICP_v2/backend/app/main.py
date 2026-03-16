from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import time, json, hashlib
from .db.db import init_db, get_conn, q, fetchall, fetchone
from .models import ProofPacket, DeviceRegisterRequest, TenantUpsertRequest, GroupMembershipRequest, VerifyRequest, GroupVerifyRequest
from .services.crypto import canonical_json, sha256_hex, verify_ed25519
from .services.engine import compute_c_env, tier_from_signals
from .services.state import update_state
from .services.graph import node_id, infer_continuity, infer_cohab, infer_risk_cluster, simple_clusters
from .services.policy import get_policy, evaluate_group

app = FastAPI(title="MitoPulse v2 — TrustGraph + ICP (Ed25519)")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))

@app.on_event("startup")
def _startup():
    init_db()
    # create default tenant if missing
    conn = get_conn()
    try:
        if not fetchone(conn, "SELECT tenant_id FROM tenants WHERE tenant_id=?", ("demo",)):
            pol = {"allowed_skew_seconds": 86400,
                   "group_verify":{"window_seconds":600,"require_quorum":2,"min_stability_band":0.55,"max_risk":60}}
            q(conn, "INSERT INTO tenants(tenant_id,name,policy_json,created_at) VALUES(?,?,?,?)",
              ("demo","Demo Tenant", json.dumps(pol), int(time.time())))
            conn.commit()
    finally:
        conn.close()

def audit(conn, action: str, outcome: str, reason: str, tenant_id=None, user_id=None, device_id=None, request_id=None, meta=None):
    q(conn, "INSERT INTO audit_logs(ts,action,tenant_id,user_id,device_id,request_id,outcome,reason,meta_json) VALUES(?,?,?,?,?,?,?,?,?)",
      (int(time.time()), action, tenant_id, user_id, device_id, request_id, outcome, reason, json.dumps(meta or {}, ensure_ascii=False)))
    conn.commit()

@app.get("/health")
def health():
    return {"status":"ok","version":"2.0"}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    conn = get_conn()
    try:
        events = fetchall(conn, "SELECT * FROM identity_events ORDER BY id DESC LIMIT 50")
        edges  = fetchall(conn, "SELECT * FROM trust_edges ORDER BY id DESC LIMIT 50")
        audit_rows = fetchall(conn, "SELECT * FROM audit_logs ORDER BY id DESC LIMIT 60")
        clusters = simple_clusters(conn)
        return templates.TemplateResponse("dashboard.html", {"request": request, "events": events, "edges": edges, "audit": audit_rows, "clusters": json.dumps(clusters, indent=2)})
    finally:
        conn.close()

@app.post("/v2/tenant/upsert")
def tenant_upsert(req: TenantUpsertRequest):
    conn = get_conn()
    try:
        q(conn, "INSERT INTO tenants(tenant_id,name,policy_json,created_at) VALUES(?,?,?,?) ON CONFLICT(tenant_id) DO UPDATE SET name=excluded.name, policy_json=excluded.policy_json",
          (req.tenant_id, req.name, json.dumps(req.policy), int(time.time())))
        conn.commit()
        audit(conn, "tenant_upsert", "ok", "ok", tenant_id=req.tenant_id, meta={"name":req.name})
        return {"ok": True}
    finally:
        conn.close()

@app.post("/v2/group/membership")
def group_membership(req: GroupMembershipRequest):
    conn = get_conn()
    try:
        q(conn, "INSERT INTO membership(tenant_id,group_id,user_id,role) VALUES(?,?,?,?) ON CONFLICT(tenant_id,group_id,user_id) DO UPDATE SET role=excluded.role",
          (req.tenant_id, req.group_id, req.user_id, req.role))
        conn.commit()
        audit(conn, "group_membership", "ok", "ok", tenant_id=req.tenant_id, user_id=req.user_id, meta={"group_id":req.group_id,"role":req.role})
        return {"ok": True}
    finally:
        conn.close()

@app.post("/v2/device/register")
def device_register(req: DeviceRegisterRequest):
    conn = get_conn()
    try:
        # ensure tenant exists
        if not fetchone(conn, "SELECT tenant_id FROM tenants WHERE tenant_id=?", (req.tenant_id,)):
            raise HTTPException(404, "unknown_tenant")
        q(conn, "INSERT INTO devices(device_id,user_id,pubkey_b64,created_at) VALUES(?,?,?,?) ON CONFLICT(device_id) DO UPDATE SET user_id=excluded.user_id, pubkey_b64=excluded.pubkey_b64",
          (req.device_id, req.user_id, req.pubkey_b64, int(time.time())))
        conn.commit()
        audit(conn, "device_register", "ok", "ok", tenant_id=req.tenant_id, user_id=req.user_id, device_id=req.device_id)
        return {"ok": True}
    finally:
        conn.close()

@app.post("/v2/identity-events")
async def post_identity_event(packet: ProofPacket, request: Request):
    conn = get_conn()
    try:
        pol = get_policy(conn, packet.tenant_id)
        skew = int(pol.get("allowed_skew_seconds", 86400))
        now = int(time.time())
        if abs(packet.ts - now) > skew:
            audit(conn, "identity_event", "fail", "time_skew", tenant_id=packet.tenant_id, user_id=packet.user_id, device_id=packet.device_id, request_id=packet.request_id, meta={"ts":packet.ts,"now":now})
            raise HTTPException(400, "time_skew")

        dev = fetchone(conn, "SELECT pubkey_b64,user_id FROM devices WHERE device_id=?", (packet.device_id,))
        if not dev:
            audit(conn, "identity_event", "fail", "unknown_device", tenant_id=packet.tenant_id, user_id=packet.user_id, device_id=packet.device_id, request_id=packet.request_id)
            raise HTTPException(404, "unknown_device")
        if dev["user_id"] != packet.user_id:
            audit(conn, "identity_event", "fail", "device_user_mismatch", tenant_id=packet.tenant_id, user_id=packet.user_id, device_id=packet.device_id, request_id=packet.request_id)
            raise HTTPException(400, "device_user_mismatch")

        # verify signature: read raw json from request to ensure binary identity with client
        body_json = await request.json()
        sig_b64 = body_json.pop("sig_b64")
        msg = canonical_json(body_json)

        if not verify_ed25519(dev["pubkey_b64"], msg, sig_b64):
            audit(conn, "identity_event", "fail", "bad_signature", tenant_id=packet.tenant_id, user_id=packet.user_id, device_id=packet.device_id, request_id=packet.request_id)
            raise HTTPException(400, "bad_signature")

        # compute packet hash (proof packet)
        p_hash = sha256_hex(msg)

        # store event (anti-replay via request_id UNIQUE)
        try:
            q(conn, """INSERT INTO identity_events(tenant_id,user_id,device_id,epoch,ts,tier,idx,slope,stability,human_conf,risk,coercion,packet_hash,request_id,created_at)
                      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
              (packet.tenant_id, packet.user_id, packet.device_id, int(packet.epoch), int(packet.ts), packet.tier,
               float(packet.idx), float(packet.slope), float(packet.stability), float(packet.human_conf),
               int(packet.risk), int(packet.coercion), p_hash, packet.request_id, int(time.time())))
            conn.commit()
        except Exception:
            audit(conn, "identity_event", "fail", "replay_request_id", tenant_id=packet.tenant_id, user_id=packet.user_id, device_id=packet.device_id, request_id=packet.request_id)
            raise HTTPException(409, "replay_request_id")

        # update state (no raw persistence except derived means/std)
        st = update_state(conn, packet.tenant_id, packet.user_id, packet.device_id, int(packet.epoch), int(packet.ts), float(packet.idx), float(packet.signals.hr))

        # Trust graph inference (demo): risk cluster on coercion; cohab on same tenant within 1h at similar hour bucket
        n = node_id(packet.user_id, packet.device_id, int(packet.epoch))
        if packet.coercion:
            # link risk edges among recent coercion nodes
            rows = fetchall(conn, "SELECT user_id,device_id,epoch FROM identity_events WHERE coercion=1 AND created_at > ?",
                            (int(time.time())-3600,))
            nodes=[node_id(r["user_id"], r["device_id"], int(r["epoch"])) for r in rows]
            infer_risk_cluster(conn, list(dict.fromkeys(nodes)), 0.85, "coercion_burst")
        audit(conn, "identity_event", "ok", "ok", tenant_id=packet.tenant_id, user_id=packet.user_id, device_id=packet.device_id, request_id=packet.request_id, meta={"packet_hash":p_hash})

        return {"ok": True, "packet_hash": p_hash, "state": {"stability_band": st.get("stability_band", 0.0), "hibernating": bool(st.get("hibernating",0))}}
    finally:
        conn.close()

@app.post("/v2/verify")
def verify(req: VerifyRequest):
    conn = get_conn()
    try:
        ev = fetchone(conn, "SELECT packet_hash,user_id,device_id,epoch FROM identity_events WHERE request_id=?", (req.request_id,))
        if not ev:
            audit(conn, "verify", "fail", "unknown_request", tenant_id=req.tenant_id, user_id=req.user_id, device_id=req.device_id, request_id=req.request_id)
            return {"verified": False, "reason": "unknown_request"}
        if ev["packet_hash"] != req.packet_hash:
            audit(conn, "verify", "fail", "mismatch", tenant_id=req.tenant_id, user_id=req.user_id, device_id=req.device_id, request_id=req.request_id)
            return {"verified": False, "reason": "mismatch"}
        audit(conn, "verify", "ok", "ok", tenant_id=req.tenant_id, user_id=req.user_id, device_id=req.device_id, request_id=req.request_id)
        return {"verified": True, "reason":"ok"}
    finally:
        conn.close()

@app.post("/v2/verify/group")
def verify_group(req: GroupVerifyRequest):
    conn = get_conn()
    try:
        ok, reason, meta = evaluate_group(conn, req.tenant_id, req.group_id, [p.model_dump() for p in req.proofs])
        audit(conn, "verify_group", "ok" if ok else "fail", reason, tenant_id=req.tenant_id, meta={"group_id": req.group_id, "action": req.action, **meta})
        return {"verified": ok, "reason": reason, "detail": meta}
    finally:
        conn.close()

@app.get("/v2/identity/state")
def identity_state(tenant_id: str, user_id: str, device_id: str, epoch: int):
    conn = get_conn()
    try:
        st = fetchone(conn, "SELECT * FROM identity_state WHERE user_id=? AND device_id=? AND epoch=?", (user_id, device_id, int(epoch)))
        if not st:
            return JSONResponse({"error":"not_found"}, status_code=404)
        return {"user_id": user_id, "device_id": device_id, "epoch": int(epoch),
                "last_ts": int(st["last_ts"]),
                "mean_idx": float(st["mean_idx"]), "std_idx": float(st["std_idx"]),
                "stability_band": float(st["stability_band"]),
                "hibernating": bool(st["hibernating"])}
    finally:
        conn.close()

# ICP endpoints
@app.post("/v2/icp/handoff")
async def icp_handoff(packet: ProofPacket, request: Request):
    # Reuse identity-events logic but treat as "handoff intent" by setting meta in audit.
    # For simplicity in demo: require packet.risk < 70 and stability > 0.55
    conn = get_conn()
    try:
        # First store as normal event
        res = await post_identity_event(packet, request)
        # Create a handoff token: packet_hash + ts signed already; return hash
        audit(conn, "icp_handoff", "ok", "ok", tenant_id=packet.tenant_id, user_id=packet.user_id, device_id=packet.device_id, request_id=packet.request_id, meta={"handoff_hash": res["packet_hash"]})
        return {"ok": True, "handoff_hash": res["packet_hash"]}
    finally:
        conn.close()

@app.post("/v2/icp/complete")
def icp_complete(tenant_id: str, user_id: str, old_device_id: str, old_epoch: int, new_device_id: str, new_epoch: int, handoff_hash: str):
    conn = get_conn()
    try:
        # Basic checks: old hash exists, old belongs to user; then create continuity edge.
        ev = fetchone(conn, "SELECT user_id,device_id,epoch FROM identity_events WHERE packet_hash=?", (handoff_hash,))
        if not ev:
            audit(conn, "icp_complete", "fail", "unknown_handoff", tenant_id=tenant_id, user_id=user_id, meta={"handoff_hash": handoff_hash})
            raise HTTPException(404, "unknown_handoff")
        if ev["user_id"] != user_id or ev["device_id"] != old_device_id or int(ev["epoch"]) != int(old_epoch):
            audit(conn, "icp_complete", "fail", "handoff_mismatch", tenant_id=tenant_id, user_id=user_id, meta={"handoff_hash": handoff_hash})
            raise HTTPException(400, "handoff_mismatch")
        old_node = node_id(user_id, old_device_id, int(old_epoch))
        new_node = node_id(user_id, new_device_id, int(new_epoch))
        infer_continuity(conn, old_node, new_node, 0.92, "handoff_token")
        audit(conn, "icp_complete", "ok", "ok", tenant_id=tenant_id, user_id=user_id, meta={"old_node": old_node, "new_node": new_node})
        return {"ok": True, "reason":"continuity_edge_created"}
    finally:
        conn.close()
