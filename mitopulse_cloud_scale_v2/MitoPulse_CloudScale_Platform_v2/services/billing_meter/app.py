from fastapi import FastAPI
import time
app = FastAPI(title="MitoPulse Billing Meter", version="2.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"billing_meter","ts":int(time.time())}

from pydantic import BaseModel
USAGE = {}

class MeterRecord(BaseModel):
    tenant_id: str
    metric: str
    qty: int = 1

@app.post("/meter/record")
def meter_record(body: MeterRecord):
    key = (body.tenant_id, body.metric)
    USAGE[key] = USAGE.get(key, 0) + body.qty
    return {"ok": True, "tenant_id": body.tenant_id, "metric": body.metric, "total": USAGE[key]}

@app.get("/meter/summary")
def meter_summary():
    return {"usage": [{"tenant_id":k[0], "metric":k[1], "total":v} for k,v in USAGE.items()]}
