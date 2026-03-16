from fastapi import FastAPI
import time

app = FastAPI(title="Gateway", version="8.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"gateway","ts":int(time.time())}

import requests
from pydantic import BaseModel

PRESENCE="http://presence_engine:8081"
RISK="http://risk_engine:8082"
AI="http://ai_detection:8083"
CLUSTER="http://cluster_engine:8084"
MONITOR="http://planetary_monitor:8090"

class Event(BaseModel):
    user_id:str
    stability:float
    human_conf:float
    risk:int

@app.post("/v8/presence")
def presence(e:Event):

    p=requests.post(f"{PRESENCE}/presence",json=e.dict()).json()
    r=requests.post(f"{RISK}/risk",json=e.dict()).json()
    a=requests.post(f"{AI}/detect",json=e.dict()).json()
    c=requests.post(f"{CLUSTER}/cluster",json=e.dict()).json()
    m=requests.post(f"{MONITOR}/observe",json=e.dict()).json()

    return {
        "presence":p,
        "risk":r,
        "ai_detection":a,
        "cluster":c,
        "planetary_monitor":m
    }
