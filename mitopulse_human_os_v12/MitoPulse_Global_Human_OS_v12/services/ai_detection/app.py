from fastapi import FastAPI
import time

app = FastAPI(title="AI Detection", version="12.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"ai_detection","ts":int(time.time())}

from pydantic import BaseModel

class AI(BaseModel):
    human_conf:float

@app.post("/detect")
def detect(a:AI):
    if a.human_conf < 0.5:
        return {"ai_suspected":True}
    return {"ai_suspected":False}
