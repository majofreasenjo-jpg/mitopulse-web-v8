from fastapi import FastAPI
import time
app = FastAPI(title="Presence Engine", version="1.0.0")
@app.get("/health")
def health():
    return {"status":"ok","service":"presence_engine","ts":int(time.time())}
from pydantic import BaseModel
class PresenceInput(BaseModel):
    stability: float
    human_conf: float
@app.post("/presence/analyze")
def analyze(body: PresenceInput):
    band="stable"
    if body.stability < 0.40: band="anomaly"
    elif body.stability < 0.70: band="drift"
    return {"band": band}
