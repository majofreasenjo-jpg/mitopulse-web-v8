from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from engine.modular_runner import run_live_profile, run_historical
import yaml

BASE_DIR = Path(__file__).resolve().parents[1]
app = FastAPI(title="MitoPulse Modular Institutional Platform v12")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def list_profiles() -> list[dict]:
    out = []
    for path in sorted((BASE_DIR / "profiles").glob("*.yaml")):
        with open(path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        out.append({
            "name": path.stem,
            "industry": cfg.get("industry"),
            "size": cfg.get("size"),
            "mode": cfg.get("mode"),
            "scenario": cfg.get("scenario"),
        })
    return out


def list_historical() -> list[str]:
    return sorted([p.stem for p in (BASE_DIR / "historical").glob("*.json")])


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "profiles": list_profiles(),
            "historical": list_historical(),
        },
    )

@app.get("/verify", response_class=HTMLResponse)
def verify_challenge(request: Request):
    return templates.TemplateResponse("verify.html", {"request": request})


@app.get("/api/profile/{profile_name}")
def profile(profile_name: str):
    return run_live_profile(profile_name)


@app.get("/api/historical/{scenario_name}")
def historical(scenario_name: str):
    return run_historical(scenario_name)
