from fastapi import FastAPI
import time

app = FastAPI(title="Cluster Engine", version="7.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"cluster_engine","ts":int(time.time())}

from pydantic import BaseModel

class Node(BaseModel):
    user_id:str

@app.post("/cluster")
def cluster(n:Node):

    return {"cluster":"planetary","node":n.user_id}
