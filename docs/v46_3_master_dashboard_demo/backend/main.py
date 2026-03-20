from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from backend.modules.master_stack import build_live_graph, executive, forecast, system_brain, ai_layer, invisible_storm, verify, add_action

app = FastAPI(title="MitoPulse v46.3 Master Dashboard")
BASE = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE / "frontend"))

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
def api_brain():
    return system_brain()

@app.get("/api/ai")
def api_ai():
    return ai_layer()

@app.get("/api/demo/invisible-storm")
def api_demo():
    return invisible_storm()

@app.get("/api/verify")
def api_verify():
    return verify()

@app.post("/api/action")
def api_action(entity_id: str = Query(...), action: str = Query(...)):
    return add_action(entity_id, action)
