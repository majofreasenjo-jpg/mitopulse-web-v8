from fastapi import FastAPI
app = FastAPI(title="Anti-Spoof Engine")
@app.get("/health")
def health(): return {"status":"ok","service":"anti_spoof"}
@app.post("/score")
def score(payload: dict):
    s = payload.get("signals", {})
    a = 0.55
    if 15 <= s.get("tap_interval_std",0) <= 250: a += 0.10
    else: a -= 0.12
    if 0.30 <= s.get("pointer_entropy",0) <= 0.95: a += 0.12
    else: a -= 0.14
    if 0.10 <= s.get("typing_variance",0) <= 0.90: a += 0.06
    if s.get("session_duration_ms",0) < 1000: a -= 0.10
    return {"anti_spoof_score": round(max(0,min(a,1)),4)}
