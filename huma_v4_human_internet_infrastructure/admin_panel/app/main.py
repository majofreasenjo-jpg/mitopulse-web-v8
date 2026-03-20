import os, httpx, json
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
app = FastAPI(title="Huma Admin Panel")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))
FEATURE_FLAG_URL = os.getenv("FEATURE_FLAG_URL","http://localhost:8011")
POLICY_URL = os.getenv("POLICY_URL","http://localhost:8007")
GATEWAY_URL = os.getenv("GATEWAY_URL","http://localhost:8000")
@app.get("/health")
def health(): return {"status":"ok","service":"admin_panel"}
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    async with httpx.AsyncClient(timeout=10.0) as client:
        tenants = (await client.get(f"{FEATURE_FLAG_URL}/tenants")).json()["tenants"]
        policies = (await client.get(f"{POLICY_URL}/policies")).json()["policies"]
        deliveries = (await client.get(f"{GATEWAY_URL}/v4/webhook-deliveries")).json()["deliveries"]
    return templates.TemplateResponse("admin.html", {"request": request, "tenants": tenants, "policies": policies, "deliveries": deliveries})
@app.post("/policy")
async def save_policy(action: str = Form(...), ok: float = Form(...), review: float = Form(...)):
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(f"{POLICY_URL}/policies", json={"action": action, "ok": ok, "review": review})
    return RedirectResponse("/", status_code=303)
@app.post("/tenant")
async def save_tenant(tenant_id: str = Form(...), features_json: str = Form(...)):
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(f"{FEATURE_FLAG_URL}/tenant", json={"tenant_id": tenant_id, "features": json.loads(features_json)})
    return RedirectResponse("/", status_code=303)
@app.post("/webhook")
async def save_webhook(tenant_id: str = Form(...), url: str = Form(...), event_type: str = Form(...)):
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(f"{GATEWAY_URL}/v4/webhooks/register", json={"tenant_id": tenant_id, "url": url, "event_type": event_type})
    return RedirectResponse("/", status_code=303)
