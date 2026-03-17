from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from engine.modular_runner import run_live_profile, run_historical, list_profiles_meta, list_historical_meta, list_demo_killers, run_demo_killer
from ingestion.client_data_loader import save_uploaded_file

BASE_DIR = Path(__file__).resolve().parents[1]
app = FastAPI(title="MitoPulse Final Modular Prototype v13")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "profiles": list_profiles_meta(),
            "historical": list_historical_meta(),
            "demos": list_demo_killers(),
        },
    )

@app.get("/verify", response_class=HTMLResponse)
def verify_challenge(request: Request):
    return templates.TemplateResponse("verify.html", {"request": request})

@app.get('/api/options')
def options():
    return {
        'profiles': list_profiles_meta(),
        'historical': list_historical_meta(),
        'demos': list_demo_killers(),
    }

@app.get("/api/profile/{profile_name}")
def profile(profile_name: str):
    return run_live_profile(profile_name)

@app.get("/api/historical/{scenario_name}")
def historical(scenario_name: str):
    return run_historical(scenario_name)

@app.get("/api/demo/{demo_name}")
def demo(demo_name: str):
    return run_demo_killer(demo_name)

@app.post('/api/upload')
async def upload(file: UploadFile = File(...)):
    return await save_uploaded_file(BASE_DIR / 'uploads', file)
