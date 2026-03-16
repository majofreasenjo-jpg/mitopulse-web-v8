
from fastapi import FastAPI

app = FastAPI(title="MitoPulse MVP Productivo v1")

@app.get("/health")
def health():
    return {"status":"MitoPulse MVP running"}

@app.get("/pilot/nodes")
def pilot_nodes():
    return {
        "pilot_ring": [
            {"id":"nd_manu_01","name":"Manuel"},
            {"id":"nd_ana_01","name":"Ana"},
            {"id":"nd_bruno_01","name":"Bruno"},
            {"id":"nd_carla_01","name":"Carla"}
        ]
    }
