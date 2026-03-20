from fastapi import FastAPI
app = FastAPI(title="Trust Engine")
@app.get("/health")
def health(): return {"status":"ok","service":"trust"}
@app.post("/score")
def score(payload: dict):
    hp = payload.get("human_probability",0)
    rs = payload.get("risk_score",0)
    cs = payload.get("continuity_score",0)
    fp = payload.get("fraud_memory_penalty",0)
    gt = payload.get("graph_trust_score",0)
    hist = payload.get("historical_trust",0.2)
    dt = payload.get("device_trust",0.5)
    m = payload.get("maturity",0.1)
    asp = payload.get("anti_spoof_score",0.5)
    rep = payload.get("reputation_score",0.2)
    idc = payload.get("identity_continuity_score",0.2)
    g = 0.14*hp + 0.10*dt + 0.10*cs + 0.08*hist + 0.08*gt + 0.06*m + 0.10*asp + 0.12*rep + 0.10*idc - 0.08*rs - 0.06*fp
    g = round(max(0,min(g,1)),4)
    level = "high" if g >= 0.85 else "medium" if g >= 0.65 else "low"
    challenge_required = True if 0.50 <= g < 0.78 else False
    return {"global_human_score": g, "trust_level": level, "challenge_required": challenge_required}
