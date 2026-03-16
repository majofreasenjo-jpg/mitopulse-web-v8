import os
import jwt
import typing
from datetime import datetime, timedelta
from fastapi import Header, HTTPException

JWT_SECRET = os.getenv("JWT_SECRET", "mitopulse-demo-secret")

def create_token(tenant_id: str):
    payload = {"tenant_id": tenant_id, "exp": datetime.utcnow() + timedelta(hours=8)}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def require_tenant_token(authorization: typing.Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload["tenant_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
