from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse human_os_kernel", version="13.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"human_os_kernel","ts":int(time.time())}
