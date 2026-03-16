from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI(title="Feature Flag Service")
TENANTS = {
    "startup_demo": {"presence_engine": True, "risk_engine": True, "continuity_engine": False, "device_trust_engine": True, "anti_spoof_engine": False, "fraud_memory": False, "graph_engine": False, "trust_engine": True, "policy_engine": True, "challenge_engine": False, "identity_continuity_protocol": False, "reputation_network": True},
    "enterprise_demo": {"presence_engine": True, "risk_engine": True, "continuity_engine": True, "device_trust_engine": True, "anti_spoof_engine": True, "fraud_memory": True, "graph_engine": True, "trust_engine": True, "policy_engine": True, "challenge_engine": True, "identity_continuity_protocol": True, "reputation_network": True},
    "sovereign_demo": {"presence_engine": True, "risk_engine": True, "continuity_engine": True, "device_trust_engine": True, "anti_spoof_engine": True, "fraud_memory": True, "graph_engine": True, "trust_engine": True, "policy_engine": True, "challenge_engine": True, "identity_continuity_protocol": True, "reputation_network": True},
}
class TenantFlags(BaseModel):
    tenant_id: str
    features: dict
@app.get("/health")
def health(): return {"status":"ok","service":"feature_flag_service"}
@app.get("/tenant/{tenant_id}")
def get_tenant(tenant_id: str): return {"tenant_id": tenant_id, "features": TENANTS.get(tenant_id, TENANTS["startup_demo"])}
@app.get("/tenants")
def list_tenants(): return {"tenants": TENANTS}
@app.post("/tenant")
def upsert_tenant(body: TenantFlags):
    TENANTS[body.tenant_id] = body.features
    return {"status":"saved","tenant_id":body.tenant_id,"features":body.features}
