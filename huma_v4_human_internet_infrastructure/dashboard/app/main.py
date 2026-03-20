import os, httpx
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
app = FastAPI(title="Huma Dashboard v4")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))
GATEWAY_URL = os.getenv("GATEWAY_URL","http://localhost:8000")
@app.get("/health")
def health(): return {"status":"ok","service":"dashboard"}
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    async with httpx.AsyncClient(timeout=10.0) as client:
        summary = (await client.get(f"{GATEWAY_URL}/v4/dashboard/summary")).json()
        events = (await client.get(f"{GATEWAY_URL}/v4/dashboard/events")).json()
        profiles = (await client.get(f"{GATEWAY_URL}/v4/dashboard/profiles")).json()
    return templates.TemplateResponse("dashboard.html", {"request": request, "summary": summary, "events": events["events"], "profiles": profiles["profiles"]})
