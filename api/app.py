from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ingestion.client_data_loader import load_client_folder
from engine.graph_builder import build_graph
from engine.evaluation import evaluate_improvement

app = FastAPI(title="MitoPulse Pilot Demo Pack v9")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/scenarios")
def scenarios():
    return {
        "industries": ["bank", "marketplace", "telco"],
        "client_sizes": ["small", "medium", "large"]
    }

@app.get("/api/demo")
def demo(industry: str = "bank", client_size: str = "small"):
    folder = f"data/{industry}_{client_size}"
    customers, devices, events, signals = load_client_folder(folder)
    G = build_graph(customers, devices, events, signals)
    result = evaluate_improvement(G, events, industry, client_size)
    result["dataset_profile"] = {
        "customers": len(customers),
        "devices": len(devices),
        "events": len(events),
        "signals": len(signals),
    }
    result["graph_stats"] = {"nodes": G.number_of_nodes(), "edges": G.number_of_edges()}
    return result
