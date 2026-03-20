from fastapi import FastAPI
import time

app = FastAPI(title="Planetary Monitor", version="11.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"planetary_monitor","ts":int(time.time())}

from pydantic import BaseModel

class Event(BaseModel):
    user_id:str

@app.post("/observe")
def observe(e:Event):
    return {
        "planetary_status":"stable",
        "node":e.user_id
    }
