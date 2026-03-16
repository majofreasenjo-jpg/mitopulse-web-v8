from fastapi import FastAPI
import time

app = FastAPI(title="Civilization Engine", version="9.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"civilization_engine","ts":int(time.time())}

from pydantic import BaseModel

class Event(BaseModel):
    user_id:str

@app.post("/analyze")
def analyze(e:Event):

    return {
        "civilization_signal":"normal_activity",
        "node":e.user_id
    }
