from pathlib import Path
import json, os
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from dotenv import load_dotenv

from backend.connectors.sources import unified_live_feed
from backend.core.ai_modules import (
    semantic_ingestion_ai, local_pattern_ai, behavioral_ai,
    evolution_ai, explainability_ai, strategy_copilot
)
from backend.core.living_core import compute_kpis, build_graph, system_brain, alerts_and_action

load_dotenv()

app = FastAPI(title="MitoPulse v43.3 Live Real")
BASE = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE / "frontend"))
DB_PATH = BASE / "backend" / "data" / "state.json"

def load_entities():
    return json.loads((BASE / "backend" / "data" / "entities.json").read_text(encoding="utf-8"))

def load_state():
    if not DB_PATH.exists():
        DB_PATH.write_text(json.dumps({"actions":[],"alerts":[]}, indent=2), encoding="utf-8")
    return json.loads(DB_PATH.read_text(encoding="utf-8"))

def save_state(state):
    DB_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/overview")
def overview(client_mode: str = Query("full")):
    entities = load_entities()
    kpis = compute_kpis(entities)
    summary = alerts_and_action(kpis, client_mode=client_mode)
    return {"kpis": kpis, "summary": summary}

@app.get("/api/graph")
def graph():
    entities = load_entities()
    return build_graph(entities)

@app.get("/api/brain")
def brain():
    entities = load_entities()
    return system_brain(entities)

@app.get("/api/ai")
def ai():
    entities = load_entities()
    normalized = semantic_ingestion_ai(entities)
    patterns = local_pattern_ai(entities)
    behavior = behavioral_ai(entities)
    kpis = compute_kpis(entities)
    summary = alerts_and_action(kpis, client_mode=os.getenv("CLIENT_MODE","full"))
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
def connectors():
    return unified_live_feed()

@app.post("/api/action/sandbox")
def action_sandbox(entity_id: str = Query(...), action: str = Query(...), recipient: str = Query("Risk Ops")):
    state = load_state()
    evt = {"entity_id": entity_id, "action": action, "recipient": recipient}
    state["actions"].append(evt)
    save_state(state)
    return {"status":"ok","event":evt,"state":state}

@app.get("/api/action/state")
def action_state():
    return load_state()

@app.get("/api/simulation")
def simulation():
    entities = load_entities()
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
    return {"steps": steps}
