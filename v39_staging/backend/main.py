
from fastapi import FastAPI
import json, time
from connectors.live import get_live

app = FastAPI()
DB="storage/db.json"

def load(): return json.load(open(DB))
def save(d): json.dump(d, open(DB,"w"), indent=2)

@app.get("/")
def root(): return {"system":"MitoPulse v39 FINAL"}

@app.get("/mode")
def mode(): return load()["mode"]

@app.post("/mode")
def set_mode(mode:str):
    db=load(); db["mode"]=mode; save(db); return {"mode":mode}

@app.get("/live")
def live(): return get_live()

@app.post("/alert")
def alert(entity:str, risk:int):
    db=load()
    rep={"entity":entity,"risk":risk,"ts":time.time()}
    db["reports"].append(rep)
    save(db)
    return rep

@app.get("/reports")
def reports(): return load()["reports"]
