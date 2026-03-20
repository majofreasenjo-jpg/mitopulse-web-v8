
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from mitopulse.core.engine import evaluate

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status":"running"}

@app.post("/evaluate")
def eval(signal: float):
    return evaluate(signal)
