
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class IdentityEvent(BaseModel):
    user:str
    device:str
    ts:int
    dynamic_id:str
    index:float
    tier:str
    risk:int

events=[]

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/v1/identity-events")
def post_event(e:IdentityEvent):
    events.append(e)
    return {"stored":True}

@app.get("/dashboard")
def dashboard():
    return {"events":[e.dict() for e in events]}
