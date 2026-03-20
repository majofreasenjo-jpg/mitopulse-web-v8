
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
    return {"system":"MitoPulse v36 Unified"}

@app.post("/alert")
def alert(entity:str, risk:int):
    db = load()
    report = {"entity":entity,"risk":risk,"ts":time.time()}
    db["reports"].append(report)
    save(db)
    return report

@app.get("/reports")
def reports():
    return load()["reports"]
