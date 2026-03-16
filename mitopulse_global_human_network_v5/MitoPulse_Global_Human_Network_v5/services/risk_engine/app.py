from fastapi import FastAPI
import time

app = FastAPI(title="Risk Engine", version="5.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"risk_engine","ts":int(time.time())}

from pydantic import BaseModel

class RiskInput(BaseModel):
    risk:int
    human_conf:float

@app.post("/risk/evaluate")
def eval_risk(r:RiskInput):
    if r.risk>80 or r.human_conf<0.6:
        return {"verdict":"block"}
    if r.risk>50:
        return {"verdict":"review"}
    return {"verdict":"ok"}
