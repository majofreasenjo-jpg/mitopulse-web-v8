from fastapi import FastAPI
app = FastAPI(title="Risk Engine")
@app.get("/health")
def health(): return {"status":"ok","service":"risk"}
@app.post("/score")
def score(payload: dict):
    s = payload.get("signals", {})
    r = 0.15
    if s.get("event_count",0) < 5: r += 0.20
    if s.get("session_duration_ms",0) < 1000: r += 0.20
    if s.get("tap_interval_std",0) < 8 and s.get("event_count",0) > 10: r += 0.25
    if s.get("pointer_entropy",0) < 0.12 and s.get("event_count",0) > 10: r += 0.20
    return {"risk_score": round(max(0,min(r,1)),4)}
