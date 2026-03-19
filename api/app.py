from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pathlib import Path
import json, math, random, time
from connectors.sources import unified_live_feed
from connectors.live_connectors import unified as unified_v35_2
from connectors.live import get_live
import os
from api.auth import login
from api.webhooks import send_webhook
from api.modules.master_stack import build_live_graph, executive, forecast, system_brain as master_brain, ai_layer, invisible_storm, verify as master_verify, add_action as master_add_action

app = FastAPI(title="MitoPulse v46.3 Master Dashboard Integrated")
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))
ROOT = Path(__file__).parent.parent
SANDBOX = {"blocked": [], "limited": [], "events": []}
DB_PATH = ROOT / "storage" / "db.json"

def load_db():
    if not DB_PATH.exists():
        return {"reports": [], "modes": {"current": "client"}}
    with open(DB_PATH) as f:
        return json.load(f)

def save_db(db):
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

def load_dataset(name: str):
    fp = ROOT / "datasets" / f"{name}.json"
    if not fp.exists():
        raise HTTPException(status_code=404, detail=f"dataset not found: {name}")
    return json.loads(fp.read_text(encoding="utf-8"))

def compute_overview(data):
    vals = [e["value"] for e in data["entities"]]
    avg = sum(vals)/max(1, len(vals))
    nhi = round(max(0, 100 - avg * 0.45), 2)
    tpi = round(min(100, avg * 0.62), 2)
    scr = round(min(100, (100-nhi)*0.4 + tpi*0.6), 2)
    mdi = round(min(100, max(vals) * 0.7), 2)
    return {"NHI": nhi, "TPI": tpi, "SCR": scr, "MDI": mdi}

def compute_brain(data):
    entities = data["entities"]
    paths = [e["id"] for e in entities if e["value"] >= 80]
    hidden_clusters = [e["id"] for e in entities if e["value"] >= 70]
    wave_nodes = [e["id"] for e in entities if e["value"] >= 60]
    return {
        "pulse_inputs": len(data["events"]),
        "cross_pulse_proxy": round(len(paths) / max(1, len(entities)), 3),
        "priority_paths": paths,
        "hidden_clusters": hidden_clusters,
        "wave_nodes": wave_nodes,
        "decision_trace": [
            "Signals ingested",
            "RFDC metrics updated",
            "Hidden coordination inferred",
            "Action threshold evaluated"
        ]
    }

def build_graph(data):
    nodes = []
    center_x, center_y = 460, 220
    ents = data["entities"]
    n = max(1, len(ents))
    for i, e in enumerate(ents):
        angle = 2 * math.pi * i / n
        radius = 150 + (e["value"] * 0.6)
        x = center_x + math.cos(angle) * radius
        y = center_y + math.sin(angle) * radius
        role = "neutral"
        if e["value"] >= 85:
            role = "trigger"
        elif e["value"] >= 70:
            role = "hidden"
        elif e["value"] >= 55:
            role = "wave"
        nodes.append({
            "id": e["id"],
            "label": e["id"],
            "kind": e["kind"],
            "x": round(x, 2),
            "y": round(y, 2),
            "score": e["value"],
            "role": role
        })
    links = []
    for ev in data["events"]:
        links.append({
            "source": ev["source"],
            "target": ev["target"],
            "weight": ev["amount"],
            "style": "solid"
        })
    dynamic_waves = [
        {
            "entity": n["id"],
            "x": n["x"],
            "y": n["y"],
            "intensity": round(n["score"] / 100, 2),
            "direction": "outward" if n["score"] >= 70 else "inward",
            "speed": round(0.7 + (n["score"]/100), 2)
        }
        for n in nodes if n["score"] >= 55
    ]
    risk_field = [
        {"x": n["x"], "y": n["y"], "intensity": round(n["score"]/100, 2)}
        for n in nodes
    ]
    trigger_zones = [n["id"] for n in nodes if n["score"] >= 85]
    return {
        "nodes": nodes,
        "links": links,
        "dynamic_waves": dynamic_waves,
        "risk_field": risk_field,
        "trigger_zones": trigger_zones
    }

def decide(data, client_type):
    overview = compute_overview(data)
    scr = overview["SCR"]
    if client_type == "marketplace":
        if scr >= 70:
            action = "Suspend seller + freeze payouts"
            channel = "Trust & Safety / Risk Ops"
        elif scr >= 45:
            action = "Manual review + payout hold"
            channel = "Trust & Safety"
        else:
            action = "Enhanced monitoring"
            channel = "Risk Analytics"
    else:
        if scr >= 70:
            action = "Freeze account / block transfer"
            channel = "Fraud / AML Unit"
        elif scr >= 45:
            action = "Manual fraud review + limits"
            channel = "Fraud Ops"
        else:
            action = "Enhanced monitoring"
            channel = "Risk Monitoring"
    return {
        "severity": "critical" if scr >= 70 else ("high" if scr >= 45 else "medium"),
        "action": action,
        "recipient": channel,
        "confidence": round(min(0.99, 0.55 + scr/200), 2)
    }

def build_report(data_name, client_type):
    data = load_dataset(data_name)
    ov = compute_overview(data)
    dec = decide(data, client_type)
    return {
        "client_type": client_type,
        "dataset": data_name,
        "summary": f"System detected coordinated risk pattern in {client_type} ecosystem.",
        "metrics": ov,
        "recipient": dec["recipient"],
        "recommended_action": dec["action"],
        "confidence": dec["confidence"],
        "alert_format": {
            "title": "MitoPulse System Alert",
            "severity": dec["severity"],
            "body": f"Action recommended: {dec['action']}. Recipient: {dec['recipient']}"
        }
    }

def build_demo(demo_id, data_name):
    data = load_dataset(data_name)
    ov = compute_overview(data)
    graph = build_graph(data)
    story_map = {
        "invisible_network": [
            "Normal ecosystem appears stable",
            "Micro-synchronizations emerge",
            "Hidden coordination becomes visible",
            "Action threshold reached"
        ],
        "invisible_storm": [
            "Weak anomalies appear",
            "Waves propagate through the graph",
            "Pressure accumulates",
            "Storm forms and action is triggered"
        ],
        "coming_collapse": [
            "System seems stable",
            "Pressure and concentration rise",
            "Collapse radar intensifies",
            "Critical zone activates intervention"
        ]
    }
    steps = []
    total = 24
    for i in range(1, total+1):
        progress = i / total
        phase = "emergence" if progress < 0.34 else ("propagation" if progress < 0.67 else "criticality")
        steps.append({
            "step": i,
            "phase": phase,
            "nhi": round(max(0, ov["NHI"] - progress*12), 2),
            "tpi": round(min(100, ov["TPI"] + progress*18), 2),
            "scr": round(min(100, ov["SCR"] + progress*22), 2),
            "story": story_map[demo_id][min(3, int(progress*4))],
            "action_triggered": progress > 0.78,
            "graph": graph
        })
    return {"demo_id": demo_id, "steps": steps}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/executive")
def api_executive():
    return executive()

@app.get("/api/live-graph")
def api_live_graph():
    return build_live_graph()

@app.get("/api/forecast")
def api_forecast(horizon: str = "short"):
    return forecast(horizon=horizon)

@app.get("/api/brain")
def api_brain_master():
    return master_brain()

@app.get("/api/ai")
def api_ai():
    return ai_layer()

@app.get("/api/demo/invisible-storm")
def api_demo():
    return invisible_storm()

@app.get("/api/verify")
def api_verify_master():
    return master_verify()

@app.post("/api/action")
def api_action(entity_id: str = Query(...), action: str = Query(...)):
    return master_add_action(entity_id, action)

@app.post("/api/action/sandbox")
def api_action_sandbox(entity_id: str = Query(...), action: str = Query(...), recipient: str = Query("Ops")):
    SANDBOX["events"].append({"entity_id": entity_id, "action": action, "recipient": recipient})
    if "freeze" in action.lower() or "block" in action.lower():
        if entity_id not in SANDBOX["blocked"]:
            SANDBOX["blocked"].append(entity_id)
    else:
        if entity_id not in SANDBOX["limited"]:
            SANDBOX["limited"].append(entity_id)
    return {"status": "ok", "sandbox": SANDBOX}

@app.get("/api/action/sandbox/state")
def api_action_state():
    return SANDBOX

@app.get("/api/connectors")
def api_connectors():
    return unified_live_feed()

@app.get("/api/demo")
def api_demo(demo_id: str = "invisible_network", dataset: str = "marketplace"):
    return build_demo(demo_id, dataset)

@app.get("/live")
def live():
    return get_live()

@app.get("/report")
def report():
    db = load_db()
    r = {"msg":"system alert","severity":"high"}
    if "reports" not in db: db["reports"] = []
    db["reports"].append(r)
    save_db(db)
    return r

@app.get("/history")
def history():
    return load_db()

@app.post("/login")
def do_login(username: str, password: str):
    return login(username, password)

@app.post("/alert")
def alert(client: str, entity: str, risk: int):
    db = load_db()
    report = {"client": client, "entity": entity, "risk": risk, "ts": time.time()}
    if "reports" not in db: db["reports"] = []
    db["reports"].append(report)
    save_db(db)
    webhook = send_webhook(report)
    return {"report": report, "webhook": webhook}

@app.get("/reports")
def reports_list():
    return load_db().get("reports", [])

@app.get("/mode")
def get_mode():
    db = load_db()
    return db.get("modes", {"current": "client"})

@app.post("/mode")
def set_mode(mode: str):
    db = load_db()
    if "modes" not in db: db["modes"] = {"current": "client"}
    db["modes"]["current"] = mode
    save_db(db)
    return db["modes"]
