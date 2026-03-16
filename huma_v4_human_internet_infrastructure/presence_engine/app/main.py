from fastapi import FastAPI
app = FastAPI(title="Presence Engine")
@app.get("/health")
def health(): return {"status":"ok","service":"presence"}
@app.post("/score")
def score(payload: dict):
    s = payload.get("signals", {})
    v = 0.50
    if s.get("event_count",0) >= 15: v += 0.10
    if 4000 <= s.get("session_duration_ms",0) <= 120000: v += 0.10
    if 20 <= s.get("tap_interval_std",0) <= 250: v += 0.12
    if 0.35 <= s.get("pointer_entropy",0) <= 0.95: v += 0.12
    if 0 <= s.get("focus_switch_count",0) <= 8: v += 0.05
    return {"human_probability": round(max(0,min(v,1)),4)}
