from fastapi import FastAPI
import time
app = FastAPI(title="Ledger Service", version="1.0.0")
@app.get("/health")
def health():
    return {"status":"ok","service":"ledger_service","ts":int(time.time())}
CHAIN=[]
@app.post("/ledger/append")
def append(body: dict):
    CHAIN.append(body)
    return {"ok":True,"size":len(CHAIN)}
@app.get("/ledger/list")
def list_entries():
    return {"entries":CHAIN[-200:]}
