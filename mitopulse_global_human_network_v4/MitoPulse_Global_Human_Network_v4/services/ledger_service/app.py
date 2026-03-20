from fastapi import FastAPI
import time

app = FastAPI(title="Ledger Service", version="4.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"ledger_service","ts":int(time.time())}

import hashlib
CHAIN = []

def hash_entry(prev_hash: str, payload: dict) -> str:
    data = (prev_hash + str(payload)).encode()
    return hashlib.sha256(data).hexdigest()

@app.post("/ledger/append")
def append(body: dict):
    prev = CHAIN[-1]["hash"] if CHAIN else "GENESIS"
    entry_hash = hash_entry(prev, body)
    entry = {"ts": int(time.time()), "prev_hash": prev, "hash": entry_hash, "payload": body}
    CHAIN.append(entry)
    return {"ok": True, "hash": entry_hash, "size": len(CHAIN)}

@app.get("/ledger/list")
def list_entries():
    return {"entries": CHAIN[-200:]}
