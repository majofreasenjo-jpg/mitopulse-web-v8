from fastapi import FastAPI
import time

app = FastAPI(title="Planetary Simulator", version="7.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"planetary_simulator","ts":int(time.time())}

from pydantic import BaseModel

class Node(BaseModel):
    user_id:str

@app.post("/simulate")
def simulate(n:Node):

    return {
        "global_state":"stable",
        "node":n.user_id
    }
