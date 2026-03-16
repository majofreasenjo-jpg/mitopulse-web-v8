from fastapi import FastAPI
app = FastAPI(title="Device Trust Engine")
@app.get("/health")
def health(): return {"status":"ok","service":"device_trust"}
@app.post("/score")
def score(payload: dict):
    known = payload.get("known_device", False)
    s = payload.get("signals", {})
    dt = 0.42 + (0.20 if known else 0)
    if s.get("screen_width",0) > 0 and s.get("screen_height",0) > 0: dt += 0.10
    if s.get("timezone"): dt += 0.08
    if s.get("language"): dt += 0.07
    return {"device_trust": round(max(0,min(dt,1)),4)}
