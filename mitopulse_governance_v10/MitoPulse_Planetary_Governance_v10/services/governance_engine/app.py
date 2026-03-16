from fastapi import FastAPI
import time

app = FastAPI(title="Governance Engine", version="10.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"governance_engine","ts":int(time.time())}

from pydantic import BaseModel

class Event(BaseModel):
    user_id:str

@app.post("/govern")
def govern(e:Event):

    return {
        "policy":"allow",
        "node":e.user_id
    }
