from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ingestion.client_data_loader import load_client_folder
from engine.graph_builder import build_graph
from engine.risk_engine import portfolio_projection, bioinspired_node_assessment
from engine.morphogenesis import morphogenetic_growth_signature

app = FastAPI(title="MitoPulse BioInspired Trust Platform v8")
templates = Jinja2Templates(directory="templates")
DATA_FOLDER = "data/sample_bank"

def run_assessment():
    customers, devices, events, signals = load_client_folder(DATA_FOLDER)
    G = build_graph(customers, devices, events, signals)
    projection = portfolio_projection(G)
    morph = morphogenetic_growth_signature(events)
    return {
        "dataset_profile": {"customers": len(customers), "devices": len(devices), "events": len(events), "signals": len(signals)},
        "graph_stats": {"nodes": G.number_of_nodes(), "edges": G.number_of_edges()},
        "portfolio": projection,
        "morphogenesis": morph
    }

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/summary")
def summary():
    return run_assessment()

@app.get("/api/node/{node_id}")
def node(node_id: str):
    customers, devices, events, signals = load_client_folder(DATA_FOLDER)
    G = build_graph(customers, devices, events, signals)
    return bioinspired_node_assessment(G, node_id)
