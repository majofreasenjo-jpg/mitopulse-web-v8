from fastapi import FastAPI
import time

app = FastAPI(title="Risk Engine", version="11.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"risk_engine","ts":int(time.time())}

from pydantic import BaseModel

class Risk(BaseModel):
    risk:int

@app.post("/risk")
def risk(r:Risk):
    if r.risk > 80:
        return {"verdict":"block"}
    if r.risk > 50:
        return {"verdict":"review"}
    return {"verdict":"ok"}
