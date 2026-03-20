from fastapi import FastAPI
import time
app = FastAPI(title="Risk Engine", version="1.0.0")
@app.get("/health")
def health():
    return {"status":"ok","service":"risk_engine","ts":int(time.time())}
from pydantic import BaseModel
class RiskInput(BaseModel):
    stability: float
    human_conf: float
    risk_signal: int
    delta: float
@app.post("/risk/evaluate")
def evaluate(body: RiskInput):
    if body.human_conf < 0.55 or body.risk_signal >= 85: return {"verdict":"BLOCK"}
    if body.delta > 0.25 or body.risk_signal >= 50 or body.stability < 0.45: return {"verdict":"REVIEW"}
    return {"verdict":"OK"}
