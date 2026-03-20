
from fastapi import FastAPI
import json, time

app = FastAPI()
DB = "storage/db.json"

def load():
    return json.load(open(DB))

def save(d):
    json.dump(d, open(DB,"w"), indent=2)

@app.get("/")
def root():
    return {"system":"MitoPulse v38 Dual Mode"}

@app.get("/mode")
def get_mode():
    return load()["modes"]

@app.post("/mode")
def set_mode(mode:str):
    db = load()
    db["modes"]["current"] = mode
    save(db)
    return db["modes"]

@app.post("/alert")
def alert(client:str, entity:str, risk:int):
    db = load()
    report = {"client":client,"entity":entity,"risk":risk,"ts":time.time()}
    db["reports"].append(report)
    save(db)
    return report

@app.get("/reports")
def reports():
    return load()["reports"]
