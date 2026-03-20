from fastapi import FastAPI
import time
app = FastAPI(title="Auth Service", version="1.0.0")
@app.get("/health")
def health():
    return {"status":"ok","service":"auth_service","ts":int(time.time())}
API_KEYS={"demo-key":"demo-tenant"}
@app.post("/auth/verify")
def verify(payload: dict):
    return {"ok": API_KEYS.get(payload.get("api_key")) == payload.get("tenant_id")}
