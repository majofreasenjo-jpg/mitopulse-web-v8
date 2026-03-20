from fastapi import FastAPI
app = FastAPI(title="Graph Engine")
@app.get("/health")
def health(): return {"status":"ok","service":"graph_engine"}
@app.post("/score")
def score(payload: dict):
    sessions = payload.get("history_sessions", 0)
    known = payload.get("known_device", False)
    risk = payload.get("risk_score", 0)
    g = 0.35
    if sessions > 2: g += 0.12
    if sessions > 5: g += 0.10
    if known: g += 0.10
    if risk > 0.45: g -= 0.12
    return {"graph_trust_score": round(max(0,min(g,1)),4)}
