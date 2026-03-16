import json, os, shutil
from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from api.db import init_db, get_db, UploadRun
from simulator.client_dataset_builder import make_dataset
from ingestion.client_data_loader import load_client_folder, dataset_profile
from engine.graph_builder import build_graph
from engine.cluster_detector import suspicious_clusters
from engine.risk_engine import decision_projection

app = FastAPI(title="MitoPulse Client Simulation Platform v4")
templates = Jinja2Templates(directory="templates")
init_db()
UPLOAD_BASE_DIR = Path(os.getenv("UPLOAD_BASE_DIR", "uploads"))
UPLOAD_BASE_DIR.mkdir(parents=True, exist_ok=True)
LAST = {}

def run_pipeline(folder: str):
    customers, devices, events, signals = load_client_folder(folder)
    profile = dataset_profile(customers, devices, events, signals)
    G = build_graph(customers, devices, events, signals)
    clusters = suspicious_clusters(G)
    decisions = decision_projection(G)
    return {
        "dataset_profile": profile,
        "graph_stats": {"nodes": G.number_of_nodes(), "edges": G.number_of_edges()},
        "clusters": clusters[:10],
        "decision_projection": decisions,
    }

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    runs = db.query(UploadRun).order_by(UploadRun.id.desc()).limit(15).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "runs": runs})

@app.get("/api/generate")
def generate(client_type: str = "bank", db: Session = Depends(get_db)):
    out = f"data/generated_{client_type}"
    generation = make_dataset(out, client_type)
    result = run_pipeline(out)
    result["generation"] = generation
    result["storage_model"] = {
        "web_ui": "solo interfaz y API",
        "uploaded_data": out,
        "processing": "backend local o cloud privado",
        "database_recommendation": "PostgreSQL para producción; CSV/Parquet para demo"
    }
    row = UploadRun(client_type=client_type, source_kind="generated", folder_path=out, summary_json=json.dumps(result))
    db.add(row); db.commit()
    global LAST
    LAST = result
    return result

@app.get("/api/load-sample")
def load_sample(client_type: str = "bank", db: Session = Depends(get_db)):
    folder = f"data/sample_{client_type}"
    result = run_pipeline(folder)
    result["sample_folder"] = folder
    row = UploadRun(client_type=client_type, source_kind="sample", folder_path=folder, summary_json=json.dumps(result))
    db.add(row); db.commit()
    global LAST
    LAST = result
    return result

@app.post("/api/upload")
async def upload_dataset(
    client_type: str = Form(...),
    customers: UploadFile = File(...),
    devices: UploadFile = File(...),
    events: UploadFile = File(...),
    signals: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    folder = UPLOAD_BASE_DIR / f"{client_type}_{len(list(UPLOAD_BASE_DIR.iterdir()))+1:03d}"
    folder.mkdir(parents=True, exist_ok=True)
    mapping = {
        "customers.csv": customers,
        "devices.csv": devices,
        "events.csv": events,
        "signals.csv": signals,
    }
    for fname, up in mapping.items():
        with open(folder / fname, "wb") as f:
            shutil.copyfileobj(up.file, f)

    result = run_pipeline(str(folder))
    result["storage_model"] = {
        "web_ui": "carga archivos vía navegador",
        "uploaded_data": str(folder),
        "processing": "backend servidor",
        "database_recommendation": "migrar a PostgreSQL en piloto/producción"
    }
    row = UploadRun(client_type=client_type, source_kind="upload", folder_path=str(folder), summary_json=json.dumps(result))
    db.add(row); db.commit()
    global LAST
    LAST = result
    return RedirectResponse(url="/", status_code=303)

@app.get("/api/last")
def last():
    return LAST

@app.get("/api/how-client-data-is-built")
def how_built():
    return {
        "bank": {
            "files": ["customers.csv", "devices.csv", "events.csv", "signals.csv"],
            "minimal_columns": {
                "customers.csv": ["customer_id"],
                "devices.csv": ["device_id", "customer_id"],
                "events.csv": ["event_id", "source_id", "target_id", "event_type", "context", "amount"],
                "signals.csv": ["signal_id", "entity_id", "signal_type", "severity"]
            }
        },
        "principle": "No cargar nombre, teléfono o email en claro. Usar hashes o IDs internos."
    }

@app.get("/api/runs")
def runs(db: Session = Depends(get_db)):
    rows = db.query(UploadRun).order_by(UploadRun.id.desc()).limit(30).all()
    return [{"id": r.id, "client_type": r.client_type, "source_kind": r.source_kind, "folder_path": r.folder_path, "created_at": r.created_at.isoformat() + "Z"} for r in rows]
