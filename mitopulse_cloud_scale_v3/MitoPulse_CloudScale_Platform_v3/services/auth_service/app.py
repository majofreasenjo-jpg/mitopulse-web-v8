from fastapi import FastAPI
import time

app = FastAPI(title="Auth Service", version="3.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"auth_service","ts":int(time.time())}

API_KEYS = {"demo-key":"demo-tenant"}

@app.post("/auth/verify")
def verify(payload: dict):
    key = payload.get("api_key")
    if key in API_KEYS:
        return {"ok":True,"tenant":API_KEYS[key]}
    return {"ok":False}
