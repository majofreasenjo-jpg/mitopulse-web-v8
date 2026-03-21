
from fastapi import FastAPI
from backend.core.pipeline import run_pipeline

app = FastAPI()

from fastapi.responses import HTMLResponse
import os

@app.get("/", response_class=HTMLResponse)
def root():
    html_path = os.path.join("frontend", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>MitoPulse V72: Frontend Not Mounted</h1>"

from pydantic import BaseModel

class SignalRequest(BaseModel):
    signal: float

@app.post("/run")
def run(req: SignalRequest):
    return run_pipeline(req.signal)
