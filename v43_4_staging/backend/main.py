from pathlib import Path
import json, os
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from dotenv import load_dotenv

from backend.connectors.sources import unified_live_feed
from backend.core.auth import login
from backend.core.state import load_state, save_state, append_audit
from backend.core.ai_modules import semantic_ingestion_ai, local_pattern_ai, behavioral_ai, evolution_ai, explainability_ai, strategy_copilot
from backend.core.living_core import compute_kpis, build_graph, system_brain, alerts_and_action, filter_entities

load_dotenv()

app = FastAPI(title="MitoPulse v43.4 Enterprise Hardening")
BASE = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE / "frontend"))

def load_entities():
    return json.loads((BASE / "backend" / "data" / "entities.json").read_text(encoding="utf-8"))

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/login")
def api_login(username: str = Query(...), password: str = Query(...)):
    result = login(username, password)
    append_audit("login_attempt", {"username": username, "status": result["status"]})
    return result

@app.get("/api/tenants")
def api_tenants():
    return json.loads((BASE / "backend" / "data" / "tenants.json").read_text(encoding="utf-8"))

@app.get("/api/overview")
def api_overview(client_mode: str = Query("full"), tenant_id: str = Query("")):
    entities = filter_entities(load_entities(), tenant_id if tenant_id else None)
    kpis = compute_kpis(entities)
    summary = alerts_and_action(kpis, client_mode=client_mode)
    append_audit("overview_requested", {"tenant_id": tenant_id, "client_mode": client_mode})
    return {"kpis": kpis, "summary": summary, "tenant_id": tenant_id}

@app.get("/api/graph")
def api_graph(tenant_id: str = Query("")):
    entities = filter_entities(load_entities(), tenant_id if tenant_id else None)
    return build_graph(entities)

@app.get("/api/brain")
def api_brain(tenant_id: str = Query("")):
    entities = filter_entities(load_entities(), tenant_id if tenant_id else None)
    return system_brain(entities)

@app.get("/api/ai")
def api_ai(client_mode: str = Query("full"), tenant_id: str = Query("")):
    entities = filter_entities(load_entities(), tenant_id if tenant_id else None)
    normalized = semantic_ingestion_ai(entities)
    patterns = local_pattern_ai(entities)
    behavior = behavioral_ai(entities)
    kpis = compute_kpis(entities)
    summary = alerts_and_action(kpis, client_mode=client_mode)
    explain = explainability_ai(summary)
    strategy = strategy_copilot(summary)
    evolution = evolution_ai()
    return {
        "semantic_ingestion_ai": normalized,
        "local_pattern_ai": patterns,
        "behavioral_ai": behavior,
        "evolution_ai": evolution,
        "explainability_ai": explain,
        "strategy_copilot": strategy
    }

@app.get("/api/connectors")
def api_connectors():
    return unified_live_feed()

@app.post("/api/action/sandbox")
def api_action(entity_id: str = Query(...), action: str = Query(...), recipient: str = Query("Risk Ops"), tenant_id: str = Query("")):
    state = load_state()
    evt = {"entity_id": entity_id, "action": action, "recipient": recipient, "tenant_id": tenant_id}
    state["actions"].append(evt)
    state["alerts"].append({"entity_id": entity_id, "action": action, "tenant_id": tenant_id})
    save_state(state)
    append_audit("sandbox_action", evt)
    return {"status": "ok", "event": evt, "state": state}

@app.get("/api/action/state")
def api_action_state():
    return load_state()

@app.get("/api/simulation")
def api_simulation(tenant_id: str = Query("")):
    entities = filter_entities(load_entities(), tenant_id if tenant_id else None)
    graph = build_graph(entities)
    steps = []
    for i in range(1, 21):
        p = i / 20
        steps.append({
            "step": i,
            "phase": "emergence" if p < 0.34 else ("propagation" if p < 0.67 else "criticality"),
            "story": "System pressure builds" if p < 0.5 else ("Coordination emerges" if p < 0.8 else "Action threshold reached"),
            "nhi": round(max(0, 72 - p * 20), 2),
            "tpi": round(min(100, 28 + p * 40), 2),
            "scr": round(min(100, 22 + p * 52), 2),
            "graph": graph
        })
    return {"steps": steps, "tenant_id": tenant_id}
