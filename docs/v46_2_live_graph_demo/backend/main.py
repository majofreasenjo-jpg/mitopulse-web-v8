from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pathlib import Path

from backend.modules.live_graph_forecast import build_live_graph, short_horizon_forecast, invisible_storm_steps

app = FastAPI(title="MitoPulse v46.2 Live Graph Forecast")
BASE = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE / "frontend"))

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/live-graph")
def api_live_graph():
    return build_live_graph()

@app.get("/api/forecast")
def api_forecast(horizon: str = "short"):
    return short_horizon_forecast(horizon=horizon)

@app.get("/api/demo/invisible-storm")
def api_demo():
    return invisible_storm_steps()
