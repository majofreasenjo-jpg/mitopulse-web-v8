import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

# Mount frontend directory for static assets (JS/CSS)
frontend_path = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

class Event(BaseModel):
    entity: str
    signal: float

@app.get("/")
def root():
    return FileResponse(str(frontend_path / "index.html"))

@app.get("/api/status")
def status_check():
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
