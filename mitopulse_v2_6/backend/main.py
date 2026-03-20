
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI(title="MitoPulse v2.6")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

state_store = {}

@app.get("/")
def root():
    return {"service":"MitoPulse","version":"2.6"}

@app.post("/v1/identity-events")
def post_event(payload:dict):

    user = payload.get("user_id")
    device = payload.get("device_id")

    idx = random.uniform(0.3,0.8)
    risk = random.randint(0,80)

    baseline = 0.6
    std = 0.08

    stability = max(0,min(1,1-abs(idx-baseline)))

    human_conf = random.uniform(0.7,0.95)

    state_store[(user,device)] = {
        "index":idx,
        "risk":risk,
        "baseline_index":baseline,
        "baseline_std":std,
        "stability":stability,
        "human_confidence":human_conf
    }

    return {"ok":True}

@app.get("/v2/identity/state")
def get_state(user_id:str,device_id:str):

    data = state_store.get((user_id,device_id))

    if not data:
        return {"error":"no_state"}

    return {
        "user_id":user_id,
        "device_id":device_id,
        **data
    }

@app.get("/v2/human-proof")
def human_proof(user_id:str,device_id:str):

    data = state_store.get((user_id,device_id))

    if not data:
        return {"human":False}

    return {
        "human": data["human_confidence"] > 0.75,
        "confidence": data["human_confidence"]
    }
