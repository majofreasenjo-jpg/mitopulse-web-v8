from fastapi import FastAPI
import time

app = FastAPI(title="Gateway", version="5.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"gateway","ts":int(time.time())}

import requests
from pydantic import BaseModel

PRESENCE="http://presence_engine:8081"
RISK="http://risk_engine:8082"

class Event(BaseModel):
    user_id:str
    stability:float
    human_conf:float
    risk:int

@app.post("/v5/presence")
def presence(e:Event):

    p=requests.post(f"{PRESENCE}/presence/analyze",json=e.dict()).json()
    r=requests.post(f"{RISK}/risk/evaluate",json=e.dict()).json()

    return {
        "presence":p,
        "risk":r
    }
