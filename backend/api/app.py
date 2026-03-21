
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

import random

@app.post("/run")
def run(req: SignalRequest):
    return run_pipeline(req.signal)

@app.get("/stream")
def stream():
    # Simulate a dynamic market/network stress pulse between 1.0 and 10.0
    signal_pulse = random.uniform(1.0, 10.0)
    
    # Fully Orchestrate the pulse through the V72 End-to-End Pipeline
    telemetry = run_pipeline(signal_pulse)
    
    # Extract the pure Protocol values calculated by the backend algorithms
    risk = telemetry["propagation"]["scr"] / 100.0
    trust = telemetry["trust"]["base_trust"]
    
    # Graph Engine: Output coordinate vectors mathematically bound to risk volatility
    nodes = [(random.random() * max(0.1, risk)) for _ in range(20)]
    edges = [(random.random() * trust) for _ in range(10)]
    
    return {
        "nodes": nodes,
        "edges": edges,
        "risk": risk,
        "trust": trust,
        "signal": round(signal_pulse, 2),
        "protocol_quorum": telemetry["federation"]["is_approved"],
        "action": telemetry["final_decision"]
    }
