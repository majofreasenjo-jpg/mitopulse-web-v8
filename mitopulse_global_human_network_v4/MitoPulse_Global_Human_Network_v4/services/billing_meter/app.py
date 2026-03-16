from fastapi import FastAPI
import time

app = FastAPI(title="Billing Meter", version="4.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"billing_meter","ts":int(time.time())}

USAGE = {}

@app.post("/meter/record")
def record(body: dict):
    key = (body["tenant_id"], body["metric"])
    USAGE[key] = USAGE.get(key, 0) + body.get("qty", 1)
    return {"ok": True, "tenant_id": body["tenant_id"], "metric": body["metric"], "total": USAGE[key]}

@app.get("/meter/summary")
def summary():
    return {"usage": [{"tenant_id": k[0], "metric": k[1], "total": v} for k, v in USAGE.items()]}
