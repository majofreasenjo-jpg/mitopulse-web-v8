
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Event(BaseModel):
    entity: str
    signal: float

@app.get("/")
def root():
    return {"status": "MitoPulse API Running"}

@app.post("/evaluate")
def evaluate(event: Event):
    decision = "block" if event.signal > 0.8 else "monitor"
    return {
        "entity": event.entity,
        "decision": decision,
        "confidence": round(0.7 + event.signal*0.3, 4)
    }

@app.get("/health")
def health():
    return {"status": "ok"}
