from fastapi import FastAPI
import time

app = FastAPI(title="Civilization Simulator", version="11.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"civilization_simulator","ts":int(time.time())}

from pydantic import BaseModel

class Event(BaseModel):
    user_id:str

@app.post("/simulate")
def simulate(e:Event):
    return {
        "simulation_state":"normal_human_activity",
        "node":e.user_id
    }
