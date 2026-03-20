
from fastapi import FastAPI
from connectors.live_connectors import unified
import json, os

app = FastAPI()

DB_PATH = "storage/db.json"

def load_db():
    with open(DB_PATH) as f:
        return json.load(f)

def save_db(db):
    with open(DB_PATH,"w") as f:
        json.dump(db,f,indent=2)

@app.get("/live")
def live():
    return unified()

@app.get("/report")
def report():
    db = load_db()
    r = {"msg":"system alert","severity":"high"}
    db["reports"].append(r)
    save_db(db)
    return r

@app.get("/history")
def history():
    return load_db()
