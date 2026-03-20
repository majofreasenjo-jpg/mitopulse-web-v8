from fastapi import FastAPI
import time

app = FastAPI(title="Developer Portal", version="4.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"developer_portal","ts":int(time.time())}

import requests
GATEWAY_URL = "http://gateway:8080"

@app.get("/portal/health")
def portal_health():
    return {"status":"ok","portal":"developer"}

@app.get("/portal/examples")
def examples():
    return {
        "health": "GET /v4/healthcheck",
        "presence": "POST /v4/presence",
        "continuity_start": "POST /v4/identity/continuity/start",
        "continuity_complete": "POST /v4/identity/continuity/complete",
    }
