from __future__ import annotations

import json
import time
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .db import init_db, connect, q, exec_
from .models import (
    ProofPacket,
    VerifyResponse,
    RegisterTenantRequest,
    RegisterDeviceRequest,
    HandoffStartRequest,
    HandoffCompleteRequest,
)
from .security import hmac_sha256_b64, constant_time_equal, sha256_hex
from .state import update_identity_state
from .trust_graph import update_graph, node_id
from .icp import build_handoff_token, verify_handoff_token

app = FastAPI(title="MitoPulse TrustGraph + ICP", version="1.0")

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@app.on_event("startup")
def _startup():
    init_db()


def now() -> int:
    return int(time.time())


def require_api_key(conn, tenant_id: str, request: Request) -> None:
    key = request.headers.get("x-api-key")
    rows = q(conn, "SELECT api_key FROM tenants WHERE tenant_id=?", (tenant_id,))
    if not rows:
        raise HTTPException(404, "unknown_tenant")
    if not key or key != rows[0]["api_key"]:
        raise HTTPException(401, "invalid_api_key")


def anti_replay(conn, tenant_id: str, request_id: str) -> None:
    try:
        exec_(
            conn,
            "INSERT INTO replay_ids(tenant_id, request_id, seen_at) VALUES(?,?,?)",
            (tenant_id, request_id, now()),
        )
    except Exception:
        raise HTTPException(409, "replay_request_id")


def get_device_secret(conn, tenant_id: str, user_id: str, device_id: str) -> str:
    rows = q(
        conn,
        "SELECT shared_secret_b64 FROM devices WHERE tenant_id=? AND user_id=? AND device_id=?",
        (tenant_id, user_id, device_id),
    )
    if not rows:
        raise HTTPException(404, "unknown_device")
    return rows[0]["shared_secret_b64"]


def audit(conn, tenant_id: str, user_id: Optional[str], device_id: Optional[str], request_id: Optional[str], action: str, outcome: str, detail: str = "") -> None:
    exec_(
        conn,
        "INSERT INTO audit_logs(tenant_id,user_id,device_id,request_id,action,outcome,detail,created_at) VALUES(?,?,?,?,?,?,?,?)",
        (tenant_id, user_id, device_id, request_id, action, outcome, detail, now()),
    )


@app.get("/health")
def health():
    return {"status": "ok", "ts": now()}


@app.post("/v1/tenants/register")
def register_tenant(body: RegisterTenantRequest):
    conn = connect()
    api_key = f"k_{sha256_hex(f'{body.tenant_id}:{time.time()}'.encode())[:24]}"
    exec_(conn, "INSERT OR REPLACE INTO tenants(tenant_id,name,api_key) VALUES(?,?,?)", (body.tenant_id, body.name, api_key))
    conn.commit(); conn.close()
    return {"tenant_id": body.tenant_id, "api_key": api_key}


@app.post("/v1/devices/register")
def register_device(body: RegisterDeviceRequest, request: Request):
    conn = connect()
    require_api_key(conn, body.tenant_id, request)
    exec_(
        conn,
        """INSERT OR REPLACE INTO devices(tenant_id,user_id,device_id,epoch,tier_hint,shared_secret_b64,created_at,last_seen_at,status)
           VALUES(?,?,?,?,?,?,?,NULL,'active')""",
        (body.tenant_id, body.user_id, body.device_id, 1, body.tier_hint, body.shared_secret_b64, now()),
    )
    audit(conn, body.tenant_id, body.user_id, body.device_id, None, "device_register", "ok")
    conn.commit(); conn.close()
    return {"ok": True}


@app.post("/v1/proof-packets", response_model=VerifyResponse)
def ingest(packet: ProofPacket, request: Request):
    conn = connect()
    require_api_key(conn, packet.tenant_id, request)
    anti_replay(conn, packet.tenant_id, packet.request_id)

    secret = get_device_secret(conn, packet.tenant_id, packet.user_id, packet.device_id)

    # verify signature over canonical payload json
    payload_bytes = json.dumps(packet.payload, separators=(",", ":")).encode("utf-8")
    expect = hmac_sha256_b64(secret, payload_bytes)
    if not constant_time_equal(packet.sig, expect):
        audit(conn, packet.tenant_id, packet.user_id, packet.device_id, packet.request_id, "ingest", "fail", "bad_sig")
        raise HTTPException(401, "bad_signature")

    # basic temporal consistency (allow 48h skew for demos)
    if abs(packet.ts - now()) > 86400 * 2:
        audit(conn, packet.tenant_id, packet.user_id, packet.device_id, packet.request_id, "ingest", "fail", "bad_ts")
        raise HTTPException(400, "timestamp_out_of_range")

    # persist event (derived only)
    payload_hash = sha256_hex(payload_bytes)
    exec_(
        conn,
        """INSERT INTO identity_events(tenant_id,user_id,device_id,epoch,ts,tier_used,index_value,dynamic_id,risk,coercion,stability,human_conf,context_fp,payload_hash,created_at)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            packet.tenant_id,
            packet.user_id,
            packet.device_id,
            packet.epoch,
            packet.ts,
            packet.tier_used,
            packet.index_value,
            packet.dynamic_id,
            int(packet.risk),
            1 if packet.coercion else 0,
            float(packet.stability),
            float(packet.human_conf),
            packet.context_fp,
            payload_hash,
            now(),
        ),
    )

    # update device last_seen
    exec_(
        conn,
        "UPDATE devices SET last_seen_at=? WHERE tenant_id=? AND user_id=? AND device_id=?",
        (now(), packet.tenant_id, packet.user_id, packet.device_id),
    )

    # update identity state
    update_identity_state(conn, packet.tenant_id, packet.user_id, packet.device_id, packet.epoch, packet.index_value, packet.dynamic_id, packet.ts)

    # update trust graph
    event_row = {
        "tenant_id": packet.tenant_id,
        "user_id": packet.user_id,
        "device_id": packet.device_id,
        "epoch": packet.epoch,
        "ts": packet.ts,
        "risk": int(packet.risk),
        "coercion": 1 if packet.coercion else 0,
        "context_fp": packet.context_fp,
    }
    update_graph(conn, packet.tenant_id, event_row)

    verdict = "ok"
    reason = "ok"
    if packet.risk >= 60 or packet.stability < 0.35:
        verdict = "suspicious"
        reason = "elevated_risk_or_low_stability"
    if packet.coercion or packet.risk >= 85:
        verdict = "fail"
        reason = "coercion_or_high_risk"

    audit(conn, packet.tenant_id, packet.user_id, packet.device_id, packet.request_id, "ingest", verdict, reason)
    conn.commit(); conn.close()
    return VerifyResponse(verdict=verdict, reason=reason)


@app.get("/v2/identity/state")
def identity_state(tenant_id: str, user_id: str, device_id: str, epoch: int = 1, request: Request = None):
    conn = connect()
    require_api_key(conn, tenant_id, request)
    rows = q(
        conn,
        "SELECT * FROM identity_state WHERE tenant_id=? AND user_id=? AND device_id=? AND epoch=?",
        (tenant_id, user_id, device_id, epoch),
    )
    if not rows:
        raise HTTPException(404, "no_state")
    return rows[0]


@app.get("/v2/trust/graph")
def trust_graph(tenant_id: str, request: Request):
    conn = connect()
    require_api_key(conn, tenant_id, request)
    edges = q(conn, "SELECT * FROM graph_edges WHERE tenant_id=? ORDER BY created_at DESC LIMIT 200", (tenant_id,))
    clusters = q(conn, "SELECT * FROM clusters WHERE tenant_id=? ORDER BY created_at DESC", (tenant_id,))
    return {"edges": edges, "clusters": clusters}


# ICP
@app.post("/v1/icp/handoff/start")
def icp_handoff_start(body: HandoffStartRequest, request: Request):
    conn = connect()
    require_api_key(conn, body.tenant_id, request)
    anti_replay(conn, body.tenant_id, body.request_id)

    secret_old = get_device_secret(conn, body.tenant_id, body.user_id, body.old_device_id)
    payload_bytes = json.dumps(body.payload, separators=(",", ":")).encode("utf-8")
    expect = hmac_sha256_b64(secret_old, payload_bytes)
    if not constant_time_equal(body.sig, expect):
        audit(conn, body.tenant_id, body.user_id, body.old_device_id, body.request_id, "icp_start", "fail", "bad_sig")
        raise HTTPException(401, "bad_signature")

    token_payload = {
        "tenant_id": body.tenant_id,
        "user_id": body.user_id,
        "old_device_id": body.old_device_id,
        "new_device_id": body.new_device_id,
        "issued_at": body.ts,
        "epoch_from": q(conn, "SELECT epoch FROM devices WHERE tenant_id=? AND user_id=? AND device_id=?", (body.tenant_id, body.user_id, body.old_device_id))[0]["epoch"],
    }
    token = build_handoff_token(token_payload, secret_old)

    audit(conn, body.tenant_id, body.user_id, body.old_device_id, body.request_id, "icp_start", "ok", "handoff_token_issued")
    conn.commit(); conn.close()
    return {"handoff_token": token}


@app.post("/v1/icp/handoff/complete")
def icp_handoff_complete(body: HandoffCompleteRequest, request: Request):
    conn = connect()
    require_api_key(conn, body.tenant_id, request)
    anti_replay(conn, body.tenant_id, body.request_id)

    # verify new device signature
    secret_new = get_device_secret(conn, body.tenant_id, body.user_id, body.new_device_id)
    payload_bytes = json.dumps(body.payload, separators=(",", ":")).encode("utf-8")
    expect = hmac_sha256_b64(secret_new, payload_bytes)
    if not constant_time_equal(body.sig, expect):
        audit(conn, body.tenant_id, body.user_id, body.new_device_id, body.request_id, "icp_complete", "fail", "bad_sig")
        raise HTTPException(401, "bad_signature")

    # handoff token must be signed by old device
    token_raw = None
    try:
        token_raw = json.loads(json.dumps({}))
    except Exception:
        pass

    # We don't know old secret directly; we infer it by reading token payload first then fetching old secret.
    import base64
    from .security import b64url_decode

    token_json = json.loads(b64url_decode(body.handoff_token).decode("utf-8"))
    token_payload = token_json["p"]
    old_device_id = token_payload["old_device_id"]
    secret_old = get_device_secret(conn, body.tenant_id, body.user_id, old_device_id)
    try:
        verified = verify_handoff_token(body.handoff_token, secret_old)
    except Exception as e:
        audit(conn, body.tenant_id, body.user_id, body.new_device_id, body.request_id, "icp_complete", "fail", str(e))
        raise HTTPException(401, "invalid_handoff_token")

    # bump epoch for new device to represent a new life-cycle if desired
    rows = q(conn, "SELECT epoch FROM devices WHERE tenant_id=? AND user_id=? AND device_id=?", (body.tenant_id, body.user_id, body.new_device_id))
    cur_epoch = int(rows[0]["epoch"]) if rows else 1
    new_epoch = cur_epoch + 1
    exec_(
        conn,
        "UPDATE devices SET epoch=? WHERE tenant_id=? AND user_id=? AND device_id=?",
        (new_epoch, body.tenant_id, body.user_id, body.new_device_id),
    )

    # write continuity edge
    src = node_id(body.user_id, old_device_id, int(token_payload["epoch_from"]))
    dst = node_id(body.user_id, body.new_device_id, new_epoch)
    exec_(
        conn,
        "INSERT INTO graph_edges(tenant_id, src_node, dst_node, edge_type, weight, created_at) VALUES(?,?,?,?,?,?)",
        (body.tenant_id, src, dst, "continuity", 0.9, now()),
    )

    audit(conn, body.tenant_id, body.user_id, body.new_device_id, body.request_id, "icp_complete", "ok", "epoch_bumped_and_continuity_edge")
    conn.commit(); conn.close()
    return {"ok": True, "new_epoch": new_epoch}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, tenant_id: str = "demo"):
    conn = connect()
    # For local dashboard, don't require api key.
    events = q(conn, "SELECT * FROM identity_events WHERE tenant_id=? ORDER BY ts DESC LIMIT 50", (tenant_id,))
    states = q(conn, "SELECT * FROM identity_state WHERE tenant_id=? ORDER BY last_ts DESC LIMIT 50", (tenant_id,))
    audit_rows = q(conn, "SELECT * FROM audit_logs WHERE tenant_id=? ORDER BY created_at DESC LIMIT 50", (tenant_id,))
    edges = q(conn, "SELECT * FROM graph_edges WHERE tenant_id=? ORDER BY created_at DESC LIMIT 50", (tenant_id,))
    clusters = q(conn, "SELECT * FROM clusters WHERE tenant_id=? ORDER BY created_at DESC", (tenant_id,))
    tenants = q(conn, "SELECT * FROM tenants ORDER BY tenant_id", ())
    conn.close()
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "tenant_id": tenant_id,
            "events": events,
            "states": states,
            "audits": audit_rows,
            "edges": edges,
            "clusters": clusters,
            "tenants": tenants,
        },
    )
