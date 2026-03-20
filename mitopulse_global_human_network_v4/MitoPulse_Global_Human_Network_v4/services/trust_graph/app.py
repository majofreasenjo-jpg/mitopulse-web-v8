from fastapi import FastAPI
import time

app = FastAPI(title="Trust Graph", version="4.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"trust_graph","ts":int(time.time())}

EDGES = []

@app.post("/graph/update")
def graph_update(body: dict):
    node = f"{body['tenant_id']}:{body['user_id']}:{body['device_id']}:{body['epoch']}"
    if body.get("context", {}).get("cluster"):
        EDGES.append({"type":"cohab","src":node,"dst":f"cluster:{body['context']['cluster']}","weight":0.6,"reason":"context_cluster"})
    if body.get("risk", 0) >= 80:
        EDGES.append({"type":"risk","src":node,"dst":"risk:high","weight":0.9,"reason":"high_risk"})
    return {"ok": True, "node": node, "edges_count": len(EDGES)}

@app.get("/graph/edges")
def edges():
    return {"edges": EDGES[-200:]}
