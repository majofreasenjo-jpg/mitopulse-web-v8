from fastapi import FastAPI
app = FastAPI(title="Identity Continuity Protocol")
@app.get("/health")
def health(): return {"status":"ok","service":"identity_continuity_protocol"}
@app.post("/score")
def score(payload: dict):
    sessions = payload.get("history_sessions", 0)
    known = payload.get("known_device", False)
    s = 0.30 + (0.18 if known else 0) + min(0.25, sessions * 0.03)
    return {"identity_continuity_score": round(max(0,min(s,1)),4)}
