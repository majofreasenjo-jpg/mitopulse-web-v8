
users = {
    "admin": {"password":"admin","role":"admin"},
    "analyst": {"password":"analyst","role":"analyst"},
    "client": {"password":"client","role":"client"}
}

def login(username,password):
    u = users.get(username)
    if u and u["password"]==password:
        return {"status":"ok","role":u["role"]}
    return {"status":"fail"}
