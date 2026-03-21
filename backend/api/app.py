
from fastapi import FastAPI
from backend.core.pipeline import run_pipeline
from backend.services.binance_client import get_ticker, get_multi_tickers
from backend.services.analysis import score_signal, impact_report, build_story

app = FastAPI()

from fastapi.responses import HTMLResponse
import os

@app.get("/", response_class=HTMLResponse)
def root():
    html_path = os.path.join("frontend", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>MitoPulse V75: Frontend Not Mounted</h1>"

from pydantic import BaseModel

class SignalRequest(BaseModel):
    signal: float

import random

@app.post("/run")
def run(req: SignalRequest):
    return run_pipeline(req.signal)

@app.get("/stream")
def stream():
    # Fetch live Binance Metrics for Bitcoin
    ticker = get_ticker("BTCUSDT")
    change_pct = ticker.get("price_change_percent", 0.0)
    
    # Calculate a Market Stress Factor based on 24h absolute volatility (scaled)
    signal_pulse = max(1.0, min(15.0, abs(change_pct) * 2.0))
    
    # Fully Orchestrate the pulse through the V72 End-to-End Pipeline
    telemetry = run_pipeline(signal_pulse)
    
    # Generate the V74 Executive Story based on the live ticker
    analysis = score_signal(ticker)
    impact = impact_report(ticker, analysis)
    story = build_story(ticker, analysis, impact)
    
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
        "action": telemetry["final_decision"],
        "btc_price": ticker.get("last_price", 0.0),
        "btc_change": change_pct,
        "story": story
    }
