from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"status":"v45.1 production ready"}
