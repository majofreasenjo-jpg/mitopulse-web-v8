
from fastapi import FastAPI
from backend.core.pipeline import run_pipeline
from backend.services.binance_client import get_ticker, get_multi_tickers
from backend.services.analysis import score_signal, impact_report, build_story

import importlib.util
import os
import networkx as nx

from engine.bioinspired_engine import bioinspired_node_risk
from core.rfdc import RelationalFieldDynamicsCore
import pandas as pd
import time

# Dynamically load the LedgerService to avoid module namespace shadowing
spec = importlib.util.spec_from_file_location("verify_ledger", os.path.join("mitopulse-verify", "backend", "services", "ledger.py"))
verify_ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_ledger)

ledger = verify_ledger.LedgerService()
rfdc_engine = RelationalFieldDynamicsCore()

app = FastAPI()

from fastapi.responses import HTMLResponse
import os

@app.get("/", response_class=HTMLResponse)
def root():
    html_path = os.path.join("frontend", "master_dashboard.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>MitoPulse V76: Master Frontend Not Mounted</h1>"

@app.get("/dashboard", response_class=HTMLResponse)
def verify_dashboard():
    html_path = os.path.join("mitopulse-verify", "dashboard", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Verify Dashboard Not Found</h1>"

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
    
    # Build Network Graph Topology (V62 Integration)
    G = nx.Graph()
    G.add_node("BTCUSDT", node_type="device", signal_severity=min(abs(change_pct)*2.0, 1.0))
    G.add_node("GodMode_Core", node_type="customer")
    G.add_edge("BTCUSDT", "GodMode_Core", label="normal", context="salary")
    
    # Calculate True Bioinspired Metrics
    bio_risk = bioinspired_node_risk(G, "BTCUSDT")
    risk = bio_risk["immune_risk_score"]
    trust = bio_risk["allostatic_reserve"]
    pulse = bio_risk["pulse_score"]
    action = bio_risk["recommended_action"]
    
    
    # Execute the V68 Relational Field Dynamics Core
    events_df = pd.DataFrame([{
        "event_id": f"evt_{int(time.time() * 1000)}",
        "timestamp": time.time(),
        "source_node": "BTCUSDT",
        "target_node": "GodMode_Orchestrator",
        "amount": ticker.get("last_price", 0.0),
        "currency": "USDT",
        "risk_score": risk * 100
    }])
    signals_df = pd.DataFrame([{
        "signal_id": f"sig_{int(time.time() * 1000)}",
        "timestamp": time.time(),
        "target_node": "BTCUSDT",
        "severity": min(abs(change_pct) * 2.0, 1.0)
    }])
    
    rfdc_output = rfdc_engine.run(events_df, signals_df, client_type="finance")
    metrics = rfdc_output["metrics"]
    
    # Overwrite the legacy V74 story with the True RFDC Execution
    story = {
        "title": f"RFDC TENSOR | SCR: {metrics['scr']} | MDI: {metrics['mdi']}",
        "narrative": rfdc_output["summary"],
        "prevented_usd": (metrics['scr'] * 1250) if action in ["BLOCK", "REVIEW"] else 0
    }
    
    # Log Cryptographic Immutable Ledger Event (V78 SQLite Integration)
    tx_id = ledger.record_event("Acme_Bank_Prod", "BTC_Live_Feed", action, f"Immune: {risk*100}% | SCR: {metrics['scr']}")
    
    # Graph Engine Vectors
    import random
    nodes = [(random.random() * max(0.1, risk)) for _ in range(20)]
    edges = [(random.random() * trust) for _ in range(10)]
    
    return {
        "nodes": nodes,
        "edges": edges,
        "risk": risk,
        "trust": trust,
        "signal": pulse,
        "action": action,
        "btc_price": ticker.get("last_price", 0.0),
        "btc_change": change_pct,
        "story": story,
        "ledger": ledger.chain[-6:] # Send the latest cryptographic blocks
    }
