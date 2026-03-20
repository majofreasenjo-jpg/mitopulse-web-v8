from fastapi import FastAPI
import time

app = FastAPI(title="Presence Engine", version="5.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"presence_engine","ts":int(time.time())}

from pydantic import BaseModel

class Presence(BaseModel):
    user_id:str
    stability:float
    human_conf:float
    risk:int

@app.post("/presence/analyze")
def analyze(p:Presence):
    band="stable"
    if p.stability<0.4:
        band="anomaly"
    elif p.stability<0.7:
        band="drift"
    return {"band":band,"human_conf":p.human_conf}
