from fastapi import FastAPI
import time

app = FastAPI(title="Presence Engine", version="9.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"presence_engine","ts":int(time.time())}

from pydantic import BaseModel

class Presence(BaseModel):
    stability:float
    human_conf:float

@app.post("/presence")
def presence(p:Presence):

    band="stable"
    if p.stability<0.4:
        band="anomaly"
    elif p.stability<0.7:
        band="drift"

    return {"band":band,"human_conf":p.human_conf}
