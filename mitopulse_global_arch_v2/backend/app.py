
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="MitoPulse Global API")

API_KEY = "mitopulse-demo-key"

class Signals(BaseModel):
    hr:int
    hrv_rmssd:int
    spo2:int
    sleep_score:int
    load:int

class IdentityEvent(BaseModel):
    user_id:str
    device_id:str
    signals:Signals

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/identity/event")
def identity_event(event:IdentityEvent, x_api_key:str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="unauthorized")

    stability = 0.42
    human_conf = 0.87
    risk = 0

    return {
        "user_id":event.user_id,
        "device_id":event.device_id,
        "stability":stability,
        "human_conf":human_conf,
        "risk":risk
    }
