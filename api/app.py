import json, os, shutil
from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from api.db import init_db, get_db, UploadRun, CaseRecord, AuditLog
from api.security import create_token, require_tenant_token
from ingestion.client_data_loader import load_client_folder, dataset_profile
from engine.graph_builder import build_graph
from engine.evaluation import evaluate_improvement

app = FastAPI(title="MitoPulse Master Pilot Platform v10")
templates = Jinja2Templates(directory="templates")
init_db()
UPLOAD_BASE_DIR = Path(os.getenv("UPLOAD_BASE_DIR", "uploads"))
UPLOAD_BASE_DIR.mkdir(parents=True, exist_ok=True)

def log_action(db: Session, tenant_id: str, action: str, payload: dict):
    db.add(AuditLog(tenant_id=tenant_id, action=action, payload_json=json.dumps(payload)))
    db.commit()

def run_scenario(folder: str, industry: str, client_size: str):
    customers, devices, events, signals = load_client_folder(folder)
    G = build_graph(customers, devices, events, signals)
    result = evaluate_improvement(G, events, industry, client_size)
    result["dataset_profile"] = dataset_profile(customers, devices, events, signals)
    result["graph_stats"] = {"nodes": G.number_of_nodes(), "edges": G.number_of_edges()}
    return result

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    runs = db.query(UploadRun).order_by(UploadRun.id.desc()).limit(20).all()
    cases = db.query(CaseRecord).order_by(CaseRecord.id.desc()).limit(15).all()
    audits = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(15).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "runs": runs, "cases": cases, "audits": audits})

@app.get("/api/auth/token")
def token(tenant_id: str):
    return {"tenant_id": tenant_id, "token": create_token(tenant_id)}

@app.get("/verify", response_class=HTMLResponse)
def verify_challenge(request: Request):
    return templates.TemplateResponse("verify.html", {"request": request})

@app.get("/api/scenario")
def scenario(industry: str = "bank", client_size: str = "small"):
    folder = f"data/{industry}_{client_size}"
    return run_scenario(folder, industry, client_size)

@app.get("/api/load-sample")
def load_sample(industry: str = "bank", client_size: str = "small", tenant_id: str = Depends(require_tenant_token), db: Session = Depends(get_db)):
    folder = f"data/{industry}_{client_size}"
    result = run_scenario(folder, industry, client_size)
    row = UploadRun(tenant_id=tenant_id, client_type=industry, client_size=client_size, source_kind="sample", folder_path=folder, summary_json=json.dumps(result))
    db.add(row); db.commit(); db.refresh(row)
    log_action(db, tenant_id, "load_sample", {"run_id": row.id, "folder": folder})
    return result

@app.post("/api/upload")
async def upload_dataset(
    tenant_id_form: str = Form(...),
    client_type: str = Form(...),
    client_size: str = Form(default="custom"),
    customers: UploadFile = File(...),
    devices: UploadFile = File(...),
    events: UploadFile = File(...),
    signals: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    folder = UPLOAD_BASE_DIR / f"{tenant_id_form}_{client_type}_{client_size}_{len(list(UPLOAD_BASE_DIR.iterdir()))+1:03d}"
    folder.mkdir(parents=True, exist_ok=True)
    mapping = {"customers.csv": customers, "devices.csv": devices, "events.csv": events, "signals.csv": signals}
    for fname, up in mapping.items():
        with open(folder / fname, "wb") as f:
            shutil.copyfileobj(up.file, f)
    result = run_scenario(str(folder), client_type, client_size)
    row = UploadRun(tenant_id=tenant_id_form, client_type=client_type, client_size=client_size, source_kind="upload", folder_path=str(folder), summary_json=json.dumps(result))
    db.add(row); db.commit(); db.refresh(row)
    log_action(db, tenant_id_form, "upload_run", {"run_id": row.id, "folder": str(folder)})
    return RedirectResponse(url="/", status_code=303)

@app.post("/api/cases/create")
def create_case(run_id: int, case_title: str, tenant_id: str = Depends(require_tenant_token), db: Session = Depends(get_db)):
    row = db.query(UploadRun).filter(UploadRun.id == run_id, UploadRun.tenant_id == tenant_id).first()
    if not row:
        return {"error": "run not found"}
    case = CaseRecord(tenant_id=tenant_id, run_id=run_id, case_title=case_title, details_json=row.summary_json)
    db.add(case); db.commit(); db.refresh(case)
    log_action(db, tenant_id, "create_case", {"case_id": case.id, "run_id": run_id})
    return {"case_id": case.id, "status": case.status}

@app.get("/api/run/{run_id}")
def run_detail(run_id: int, tenant_id: str = Depends(require_tenant_token), db: Session = Depends(get_db)):
    row = db.query(UploadRun).filter(UploadRun.id == run_id, UploadRun.tenant_id == tenant_id).first()
    return json.loads(row.summary_json) if row else {"error": "run not found"}

@app.get("/api/runs")
def runs(tenant_id: str = Depends(require_tenant_token), db: Session = Depends(get_db)):
    rows = db.query(UploadRun).filter(UploadRun.tenant_id == tenant_id).order_by(UploadRun.id.desc()).limit(40).all()
    return [{"id": r.id, "client_type": r.client_type, "client_size": r.client_size, "source_kind": r.source_kind, "folder_path": r.folder_path, "created_at": r.created_at.isoformat() + "Z"} for r in rows]
