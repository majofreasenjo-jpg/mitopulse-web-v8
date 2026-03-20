from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse Gateway", version="3.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"gateway","ts":int(time.time())}

from fastapi import Header
import requests

IDENTITY_URL = "http://identity_engine:8081"
AUTH_URL = "http://auth_service:8089"

@app.get("/v3/healthcheck")
def healthcheck():
    return {"status":"gateway_ok"}

@app.post("/v3/presence")
def presence_event(payload: dict, x_api_key: str | None = Header(default=None)):
    auth = requests.post(f"{AUTH_URL}/auth/verify", json={"api_key": x_api_key}).json()
    if not auth.get("ok"):
        return {"error":"unauthorized"}

    identity = requests.post(f"{IDENTITY_URL}/identity/evaluate", json=payload).json()
    return {"ok":True,"identity":identity}
