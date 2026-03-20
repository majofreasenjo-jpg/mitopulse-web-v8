
from fastapi import FastAPI
from mitopulse.core.engine import evaluate

app = FastAPI()

@app.get("/")
def root():
    return {"status":"running"}

@app.post("/evaluate")
def eval(signal: float):
    return {"decision": evaluate(signal)}
