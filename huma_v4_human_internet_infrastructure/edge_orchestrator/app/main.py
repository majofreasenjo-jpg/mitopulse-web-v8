import os, httpx
from fastapi import FastAPI
app = FastAPI(title="Edge Orchestrator")
GATEWAY_URL = os.getenv("GATEWAY_URL","http://localhost:8000")
@app.get("/health")
def health(): return {"status":"ok","service":"edge_orchestrator"}
@app.post("/forward")
async def forward(payload: dict):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{GATEWAY_URL}/v4/verify-human", json=payload)
    return r.json()
