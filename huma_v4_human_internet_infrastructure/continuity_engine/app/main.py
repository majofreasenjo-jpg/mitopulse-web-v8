from fastapi import FastAPI
app = FastAPI(title="Continuity Engine")
@app.get("/health")
def health(): return {"status":"ok","service":"continuity"}
@app.post("/score")
def score(payload: dict):
    known = payload.get("known_device", False)
    hist = payload.get("history_sessions", 0)
    c = 0.45 + (0.22 if known else 0) + (0.12 if hist > 3 else 0)
    s = payload.get("signals", {})
    if s.get("timezone"): c += 0.08
    if s.get("language"): c += 0.08
    return {"continuity_score": round(max(0,min(c,1)),4)}
