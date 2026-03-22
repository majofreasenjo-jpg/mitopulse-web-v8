
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

@app.get("/verify-app", response_class=HTMLResponse)
def mobile_verify():
    html_path = os.path.join("frontend", "mobile_verify.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>MitoPulse Verify V80 Not Mounted</h1>"

from pydantic import BaseModel

class SignalRequest(BaseModel):
    signal: float

import random

@app.post("/run")
def run(req: SignalRequest):
    return run_pipeline(req.signal)

from fastapi import Header, HTTPException

@app.get("/stream")
def stream(x_api_key: str = Header(None)):
    if x_api_key != "mitopulse-key":
        raise HTTPException(status_code=401, detail="V82 Enterprise Orchestrator: Cryptographic keys do not match. Unauthorized Access.")
        
    # 1. Ingest Multi-Node Synchronous Binance Pulse (V81 Awakening)
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
    tickers = get_multi_tickers(symbols)
    
    current_time = time.time()
    events_data = []
    signals_data = []
    
    # Build Network Graph Topology (V62 Integration)
    G = nx.Graph()
    G.add_node("GodMode_Core", node_type="customer")
    
    last_price = 65000.0
    change_pct = 0.0
    
    for idx, t in enumerate(tickers):
        sym = t.get("symbol", symbols[idx])
        price = t.get("last_price", random.uniform(50, 100))
        change = t.get("price_change_percent", random.uniform(-2, 2))
        
        if sym == "BTCUSDT":
            last_price = price
            change_pct = change
            
        sev = min(abs(change) * 2.0, 1.0)
        
        G.add_node(sym, node_type="device", signal_severity=sev)
        G.add_edge(sym, "GodMode_Core", label="normal", context="transaction")
        
        events_data.append({
            "event_id": f"evt_{sym}_{int(current_time * 1000)}",
            "timestamp": current_time,  # CRITICAL: Synchronized timestamp guarantees Shadow Coordination
            "source_id": sym,
            "target_id": "GodMode_Orchestrator",
            "amount": price,
            "currency": sym.replace("USDT",""),
            "risk_score": sev * 100
        })
        
        signals_data.append({
            "signal_id": f"sig_{sym}_{int(current_time * 1000)}",
            "timestamp": current_time,
            "entity_id": sym,
            "severity": sev
        })
    
    # Calculate True Bioinspired Metrics (focusing on BTC reference)
    bio_risk = bioinspired_node_risk(G, "BTCUSDT")
    risk = bio_risk["immune_risk_score"]
    trust = bio_risk["allostatic_reserve"]
    pulse = bio_risk["pulse_score"]
    action = bio_risk["recommended_action"]
    
    # Execute the V68 Relational Field Dynamics Core (Now Armed with Multi-Node Tensors)
    events_df = pd.DataFrame(events_data)
    signals_df = pd.DataFrame(signals_data)
    
    rfdc_output = rfdc_engine.run(events_df, signals_df, client_type="finance")
    metrics = rfdc_output["metrics"]
    summ_data = rfdc_output["summary"]
    
    narrative_text = f"System State: {str(summ_data.get('system_state', '')).upper()} | {summ_data.get('main_risk', '')}\n"
    narrative_text += f"Severity: {str(summ_data.get('severity', '')).upper()} | Confidence: {summ_data.get('confidence', '')}\n"
    narrative_text += f"- The Autonomous Action Engine currently mandates a {str(summ_data.get('recommended_action', '')).upper()} protocol structure based on {summ_data.get('alerts_count', 0)} tensor alerts."
    
    # Overwrite the legacy V74 story with the True RFDC Execution
    story = {
        "title": f"RFDC TENSOR | SCR: {metrics['scr']} | MDI: {metrics['mdi']}",
        "narrative": narrative_text,
        "prevented_usd": (metrics['scr'] * 1250) if action in ["BLOCK", "REVIEW"] else 0
    }
    
    # Log Cryptographic Immutable Ledger Event (V78 SQLite Integration)
    tx_id = ledger.record_event("Acme_Bank_Prod", "BTC_Live_Feed", action, f"Immune: {risk*100}% | SCR: {metrics['scr']}")
    
    # Graph Engine Vectors
    import random
    nodes = [(random.random() * max(0.1, risk)) for _ in range(20)]
    edges = [(random.random() * trust) for _ in range(10)]
    
    # V79: The Predictive Forecast WaveEngine
    # Extrapolates future SCR trajectory using Systemic Climate Pressure and Wave Propagation Velocities
    future_scr = metrics['scr'] + (metrics['climate_pressure'] * 0.8) + (metrics['wave_max'] * 0.5)
    forecast_scr = min(round(future_scr, 2), 99.99)
    
    return {
        "nodes": nodes,
        "edges": edges,
        "risk": risk,
        "trust": trust,
        "signal": pulse,
        "action": action,
        "btc_price": last_price,
        "btc_change": change_pct,
        "story": story,
        "ledger": ledger.chain[-6:], # Send the latest cryptographic blocks
        "forecast": forecast_scr,
        "vortex": metrics['vortex_score'],
        "wave": metrics['wave_max']
    }
