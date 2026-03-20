
from fastapi import FastAPI
import json
from app.auth import login
from app.webhooks import send_webhook

app = FastAPI()
DB_PATH = "storage/db.json"

def load_db():
    return json.load(open(DB_PATH))

def save_db(db):
    json.dump(db,open(DB_PATH,"w"),indent=2)

@app.get("/")
def root():
    return {"msg":"MitoPulse v35.3 production"}

@app.post("/login")
def do_login(username:str,password:str):
    return login(username,password)

@app.post("/alert")
def alert(entity:str, risk:int):
    db = load_db()
    report = {"entity":entity,"risk":risk}
    db["reports"].append(report)
    save_db(db)
    webhook = send_webhook(report)
    return {"report":report,"webhook":webhook}

@app.get("/history")
def history():
    return load_db()
