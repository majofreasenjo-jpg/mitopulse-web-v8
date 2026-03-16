from fastapi import FastAPI
import time
app = FastAPI(title="Device Registry", version="1.0.0")
@app.get("/health")
def health():
    return {"status":"ok","service":"device_registry","ts":int(time.time())}
from pydantic import BaseModel
DEVICES={}
class DeviceRegister(BaseModel):
    tenant_id:str
    user_id:str
    device_id:str
    public_key:str
@app.post("/devices/register")
def register(body: DeviceRegister):
    DEVICES[(body.tenant_id, body.user_id, body.device_id)] = body.public_key
    return {"ok":True}
@app.get("/devices/public_key")
def public_key(tenant_id:str, user_id:str, device_id:str):
    pk=DEVICES.get((tenant_id,user_id,device_id))
    return {"public_key":pk} if pk else {"error":"not_found"}
