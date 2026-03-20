from fastapi import FastAPI
import time

app = FastAPI(title="Consciousness Engine", version="13.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"consciousness_engine","ts":int(time.time())}

from pydantic import BaseModel

class Signal(BaseModel):
    user_id:str
    stability:float
    human_conf:float

@app.post("/collective_state")
def collective_state(s:Signal):

    state="stable"

    if s.stability < 0.4:
        state="collective_anomaly"

    return {
        "collective_state": state,
        "node": s.user_id
    }
