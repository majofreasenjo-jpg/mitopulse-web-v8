from fastapi import FastAPI
app = FastAPI(title="Challenge Engine")
@app.get("/health")
def health(): return {"status":"ok","service":"challenge_engine"}
@app.post("/evaluate")
def evaluate(payload: dict):
    reaction_latency_ms = payload.get("reaction_latency_ms", 240)
    gesture_adjustment_score = payload.get("gesture_adjustment_score", 0.80)
    trajectory_entropy = payload.get("trajectory_entropy", 0.65)
    s = 0.45
    if 120 <= reaction_latency_ms <= 1200: s += 0.20
    else: s -= 0.15
    if 0.45 <= gesture_adjustment_score <= 1.0: s += 0.18
    else: s -= 0.10
    if 0.30 <= trajectory_entropy <= 1.0: s += 0.15
    else: s -= 0.12
    s = round(max(0,min(s,1)),4)
    return {"challenge_score": s, "challenge_passed": s >= 0.72}
