from fastapi import FastAPI
import time

app = FastAPI(title="Auth Service", version="4.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"auth_service","ts":int(time.time())}

API_KEYS = {
    "demo-key": "demo",
    "enterprise-key": "enterprise"
}

@app.post("/auth/verify")
def verify(payload: dict):
    key = payload.get("api_key")
    tenant_id = payload.get("tenant_id")
    if key in API_KEYS and API_KEYS[key] == tenant_id:
        return {"ok": True, "tenant_id": tenant_id}
    return {"ok": False}
