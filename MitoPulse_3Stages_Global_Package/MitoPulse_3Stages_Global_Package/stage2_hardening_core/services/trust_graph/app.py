from fastapi import FastAPI
import time
app = FastAPI(title="Trust Graph", version="1.0.0")
@app.get("/health")
def health():
    return {"status":"ok","service":"trust_graph","ts":int(time.time())}
EDGES=[]
@app.post("/graph/link")
def link(body: dict):
    EDGES.append(body)
    return {"ok":True}
@app.get("/graph/edges")
def edges():
    return {"edges":EDGES[-200:]}
