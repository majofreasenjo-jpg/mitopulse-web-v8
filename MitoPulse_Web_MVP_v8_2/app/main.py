import os, time, uuid, math, random, asyncio
from collections import defaultdict, deque
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mitopulse_v82.db")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def now(): return int(time.time())
def make_id(prefix): return f"{prefix}_{uuid.uuid4().hex[:10]}"
def clamp(v, a, b): return max(a, min(b, v))
def decay(score, last_ts, lam=0.0008):
    if not last_ts: return score
    return round(score * math.exp(-lam * max(0, now() - int(last_ts))), 2)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
    created_at = Column(Integer)
    nodal_mass = Column(Float, default=10.0)
    last_active_at = Column(Integer)
    status = Column(String, default="active")

class DeviceNode(Base):
    __tablename__ = "device_nodes"
    id = Column(String, primary_key=True)
    user_id = Column(String)
    platform = Column(String, default="web")
    created_at = Column(Integer)
    last_seen_at = Column(Integer)
    pulse_count = Column(Integer, default=0)
    cross_pulse_count = Column(Integer, default=0)
    status = Column(String, default="active")

class Relationship(Base):
    __tablename__ = "relationships"
    id = Column(String, primary_key=True)
    user_a = Column(String)
    user_b = Column(String)
    weight = Column(Float, default=20.0)
    interactions = Column(Integer, default=0)
    last_interaction_at = Column(Integer)
    created_at = Column(Integer)

class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(String, primary_key=True)
    event_id = Column(String)
    user_id = Column(String)
    target_id = Column(String)
    scenario = Column(String)
    source = Column(String)
    expected_label = Column(String)
    human_presence = Column(Float)
    freedom_score = Column(Float)
    relational_trust = Column(Float)
    shared_reality = Column(Float)
    context_risk = Column(Float)
    mitopulse_score = Column(Float)
    decision = Column(String)
    guardian_alert = Column(Integer, default=0)
    created_at = Column(Integer)

class CrossPulse(Base):
    __tablename__ = "cross_pulses"
    id = Column(String, primary_key=True)
    node_a = Column(String)
    node_b = Column(String)
    shared_context_score = Column(Float)
    temporal_delta_ms = Column(Float)
    source = Column(String)
    created_at = Column(Integer)

def init_db():
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="MitoPulse Web MVP v8.2")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/app", StaticFiles(directory=os.path.join(BASE_DIR, "webapp"), html=True), name="webapp")

class WSManager:
    def __init__(self): self.connections=[]
    async def connect(self, ws):
        await ws.accept(); self.connections.append(ws)
    def disconnect(self, ws):
        if ws in self.connections: self.connections.remove(ws)
    async def broadcast(self, payload):
        dead=[]
        for ws in self.connections:
            try: await ws.send_json(payload)
            except: dead.append(ws)
        for ws in dead: self.disconnect(ws)

manager = WSManager()
SIM = {"running": False, "tick": 0, "task": None}

def get_user(db, uid): return db.query(User).filter(User.id == uid).first()
def get_node(db, node_id): return db.query(DeviceNode).filter(DeviceNode.id == node_id).first()

def get_rel(db, a, b):
    rel = db.query(Relationship).filter(
        ((Relationship.user_a == a) & (Relationship.user_b == b)) |
        ((Relationship.user_a == b) & (Relationship.user_b == a))
    ).first()
    if not rel:
        rel = Relationship(id=make_id("rel"), user_a=a, user_b=b, weight=20.0, interactions=0, created_at=now())
        db.add(rel); db.flush()
    return rel

def neighbors(db, uid):
    rels = db.query(Relationship).filter((Relationship.user_a == uid) | (Relationship.user_b == uid)).all()
    return [(r.user_b if r.user_a == uid else r.user_a, r.weight) for r in rels]

def human_presence(p):
    duration = max(0.1, (time.time()*1000 - int(p.get("started_at", int(time.time()*1000)))) / 1000.0)
    clicks = int(p.get("click_count", 0)); keys = int(p.get("key_count", 0)); moves = int(p.get("move_count", 0))
    entropy = float(p.get("interaction_entropy", 0)); hesitation = float(p.get("hesitation", 0))
    s = 20 + min(20, (clicks + keys) * 2.2) + min(15, moves * 0.08) + min(15, duration * 2.8) + min(20, entropy * 35) + min(10, hesitation * 20)
    return round(clamp(s, 0, 100), 2)

def freedom_score(p):
    urgency = float(p.get("urgency", 0)); dictation = float(p.get("dictation_risk", 0)); routine = float(p.get("routine_break", 0)); hesitation = float(p.get("hesitation", 0))
    return round(clamp(100 - (urgency*30 + dictation*35 + routine*20 - hesitation*8), 0, 100), 2)

def shared_reality(p):
    vals = [float(p.get("social_overlap", 0)), float(p.get("temporal_alignment", 0)), float(p.get("context_fit", 0)), float(p.get("interaction_coherence", 0))]
    return round(clamp(sum(vals) * 25, 0, 100), 2)

def relational_trust(db, a, b, scenario, amount):
    u = get_user(db, a); t = get_user(db, b) if b else None
    if not u: return 0.0
    if not t: return 25.0
    rel = get_rel(db, a, b)
    direct = decay(rel.weight, rel.last_interaction_at)
    nu, nt = neighbors(db, a), neighbors(db, b)
    cross = ((sum(w for _, w in nu) / max(1, len(nu))) + (sum(w for _, w in nt) / max(1, len(nt)))) / 2 if (nu or nt) else 0
    social = 100 if rel.interactions > 3 else (65 if rel.interactions > 0 else 25)
    nodal = clamp(math.sqrt(max(u.nodal_mass, 1) * max(t.nodal_mass, 1)), 0, 100)
    scenario_fit = 35 if scenario in ("pass_transfer","marketplace","identity_spoof","phone_scam","sms_phish","email_phish") and rel.interactions == 0 and amount > 0 else 80
    return round(clamp(0.30*direct + 0.20*cross + 0.20*social + 0.15*nodal + 0.15*scenario_fit, 0, 100), 2)

def context_risk(p):
    return round(clamp(float(p.get("network_anomaly", 0))*35 + float(p.get("transaction_novelty", 0))*35 + float(p.get("remote_capture_probability", 0))*30, 0, 100), 2)

def classify(score):
    if score >= 80: return "VERIFY"
    if score >= 60: return "REVIEW"
    return "BLOCK"

def register_node(db, node_id, user_id=None, platform="web"):
    node = get_node(db, node_id)
    if not node:
        node = DeviceNode(id=node_id, user_id=user_id, platform=platform, created_at=now(), last_seen_at=now(), status="active")
        db.add(node)
    else:
        if user_id: node.user_id = user_id
        if platform: node.platform = platform
        node.last_seen_at = now()
        node.status = "active"
    return node

def write_pulse(db, node_id, user_id=None, platform="web"):
    node = register_node(db, node_id, user_id, platform)
    node.last_seen_at = now()
    node.pulse_count = (node.pulse_count or 0) + 1
    return node

def write_cross_pulse(db, node_a, node_b, shared_score, temporal_delta_ms=0.0, source="manual"):
    db.add(CrossPulse(
        id=make_id("xp"),
        node_a=node_a,
        node_b=node_b,
        shared_context_score=round(shared_score, 2),
        temporal_delta_ms=round(temporal_delta_ms, 2),
        source=source,
        created_at=now()
    ))
    na, nb = get_node(db, node_a), get_node(db, node_b)
    if na: na.cross_pulse_count = (na.cross_pulse_count or 0) + 1
    if nb: nb.cross_pulse_count = (nb.cross_pulse_count or 0) + 1
    if na and nb and na.user_id and nb.user_id and na.user_id != nb.user_id and get_user(db, na.user_id) and get_user(db, nb.user_id):
        rel = get_rel(db, na.user_id, nb.user_id)
        rel.interactions += 1
        rel.last_interaction_at = now()
        rel.weight = round(clamp(rel.weight + max(0.5, shared_score / 20.0), 1, 100), 2)

def evaluate(db, p, source="manual", expected_label=None):
    hp = human_presence(p); fs = freedom_score(p); sr = shared_reality(p); rt = relational_trust(db, p["user_id"], p.get("target_id"), p.get("scenario", "generic"), float(p.get("amount", 0) or 0)); cr = context_risk(p)
    score = round(clamp(0.18*hp + 0.24*fs + 0.22*sr + 0.24*rt + 0.12*(100-cr), 0, 100), 2)
    dec = classify(score)
    galert = 1 if p.get("scenario") in ("phone_scam","identity_spoof","sms_phish","email_phish") and (fs < 45 or sr < 40 or rt < 35) else 0
    db.add(Evaluation(id=make_id("eval"), event_id=make_id("evt"), user_id=p["user_id"], target_id=p.get("target_id"), scenario=p.get("scenario", "generic"), source=source, expected_label=expected_label, human_presence=hp, freedom_score=fs, relational_trust=rt, shared_reality=sr, context_risk=cr, mitopulse_score=score, decision=dec, guardian_alert=galert, created_at=now()))
    u = get_user(db, p["user_id"])
    if u:
        u.last_active_at = now()
        u.nodal_mass = clamp(u.nodal_mass + (2 if dec == "VERIFY" else (-1 if dec == "BLOCK" else 0.2)), 1, 100)
    if p.get("target_id") and get_user(db, p["target_id"]):
        t = get_user(db, p["target_id"])
        t.last_active_at = now()
        t.nodal_mass = clamp(t.nodal_mass + (0.6 if dec == "VERIFY" else (-0.3 if dec == "BLOCK" else 0.1)), 1, 100)
        rel = get_rel(db, p["user_id"], p["target_id"])
        rel.interactions += 1
        rel.last_interaction_at = now()
        rel.weight = round(clamp(rel.weight + (4 if dec == "VERIFY" else (-2 if dec == "BLOCK" else 0.5)), 1, 100), 2)
    return {"decision": dec, "mitopulse_score": score, "human_presence": hp, "freedom_score": fs, "relational_trust": rt, "shared_reality": sr, "context_risk": cr, "guardian_alert": galert}

def scenario_payload(db, scenario):
    users = db.query(User).all()
    if len(users) < 2: return None, None
    a = random.choice(users); b = random.choice([u for u in users if u.id != a.id])
    cfg = {
        "fair_payment":("legit",(0.0,0.2),(0.0,0.1),(0.1,0.3),(0.2,0.5),(0.7,1.0),(0.7,1.0),(0.7,1.0),(0.0,0.1),(0.4,0.8),(0.0,0.1),(5,40)),
        "legit_transfer":("legit",(0.0,0.2),(0.0,0.1),(0.0,0.2),(0.6,1.0),(0.7,1.0),(0.7,1.0),(0.7,1.0),(0.0,0.1),(0.0,0.4),(0.0,0.1),(20,300)),
        "phone_scam":("fraud",(0.7,1.0),(0.5,1.0),(0.5,1.0),(0.0,0.3),(0.1,0.4),(0.1,0.4),(0.2,0.5),(0.2,0.5),(0.7,1.0),(0.3,0.8),(100,900)),
        "identity_spoof":("fraud",(0.5,0.9),(0.2,0.7),(0.6,1.0),(0.0,0.2),(0.2,0.5),(0.2,0.5),(0.2,0.6),(0.1,0.4),(0.6,1.0),(0.1,0.5),(0,300)),
        "sms_phish":("fraud",(0.6,0.9),(0.2,0.6),(0.4,0.8),(0.0,0.3),(0.2,0.5),(0.2,0.5),(0.3,0.6),(0.2,0.4),(0.7,1.0),(0.2,0.5),(20,500)),
        "email_phish":("fraud",(0.4,0.8),(0.1,0.5),(0.3,0.7),(0.0,0.3),(0.2,0.6),(0.2,0.6),(0.3,0.7),(0.1,0.3),(0.6,0.9),(0.1,0.4),(20,700))
    }[scenario]
    label, urg, dicta, rout, soc, temp, ctx, coh, net, nov, rem, amt = cfg
    return {
        "user_id": a.id, "target_id": b.id, "scenario": scenario, "amount": random.randint(*amt),
        "started_at": int(time.time()*1000)-random.randint(1200,7000), "click_count": random.randint(3,15), "key_count": random.randint(0,12), "move_count": random.randint(20,120),
        "interaction_entropy": round(random.uniform(0.2,0.9),2), "hesitation": round(random.uniform(0.05,0.6),2),
        "urgency": round(random.uniform(*urg),2), "dictation_risk": round(random.uniform(*dicta),2), "routine_break": round(random.uniform(*rout),2),
        "social_overlap": round(random.uniform(*soc),2), "temporal_alignment": round(random.uniform(*temp),2), "context_fit": round(random.uniform(*ctx),2), "interaction_coherence": round(random.uniform(*coh),2),
        "network_anomaly": round(random.uniform(*net),2), "transaction_novelty": round(random.uniform(*nov),2), "remote_capture_probability": round(random.uniform(*rem),2)
    }, label

async def auto_loop():
    while SIM["running"]:
        db = SessionLocal()
        try:
            mode = random.choices(["scenario","crosspulse","pulse"], weights=[4,1,1], k=1)[0]
            if mode == "scenario":
                scenario = random.choice(["legit_transfer","fair_payment","phone_scam","identity_spoof","sms_phish","email_phish"])
                p, label = scenario_payload(db, scenario)
                if p: evaluate(db, p, "auto", label)
            elif mode == "crosspulse":
                nodes = db.query(DeviceNode).all()
                if len(nodes) >= 2:
                    a, b = random.sample(nodes, 2)
                    write_cross_pulse(db, a.id, b.id, random.uniform(60,95), random.uniform(20,220), "auto")
            else:
                nodes = db.query(DeviceNode).all()
                if nodes:
                    n = random.choice(nodes)
                    write_pulse(db, n.id, n.user_id, n.platform)
            db.commit(); SIM["tick"] += 1
        finally:
            db.close()
        await manager.broadcast({"type":"refresh","tick":SIM["tick"]})
        await asyncio.sleep(2.0)

def graph_data(db):
    users = db.query(User).all(); rels = db.query(Relationship).all()
    adj = defaultdict(list)
    for r in rels: adj[r.user_a].append(r.user_b); adj[r.user_b].append(r.user_a)
    comp = {}; cid = 0
    for u in users:
        if u.id in comp: continue
        cid += 1; q = deque([u.id]); comp[u.id] = cid
        while q:
            cur = q.popleft()
            for nxt in adj[cur]:
                if nxt not in comp:
                    comp[nxt] = cid; q.append(nxt)
    masses = sorted([u.nodal_mass for u in users], reverse=True)
    cut = masses[max(0, min(len(masses)-1, max(0, len(masses)//5-1)))] if masses else 999
    return {"nodes":[{"id":u.id,"label":u.name,"mass":round(u.nodal_mass,2),"cluster":comp.get(u.id,0),"guardian":u.nodal_mass>=cut and len(users)>=5} for u in users],
            "links":[{"source":r.user_a,"target":r.user_b,"weight":round(r.weight,2)} for r in rels]}

def metrics(db):
    rows = db.query(Evaluation).all()
    legit = [r for r in rows if r.expected_label == "legit"]; fraud = [r for r in rows if r.expected_label == "fraud"]
    fp = sum(1 for r in legit if r.decision == "BLOCK"); fn = sum(1 for r in fraud if r.decision == "VERIFY")
    legit_ok = sum(1 for r in legit if r.decision != "BLOCK"); fraud_ok = sum(1 for r in fraud if r.decision != "VERIFY")
    evals = len(legit) + len(fraud); accuracy = round(((legit_ok + fraud_ok) / evals) * 100, 2) if evals else 0
    return {"users": db.query(User).count(), "nodes": db.query(DeviceNode).count(), "cross_pulses": db.query(CrossPulse).count(), "verify": sum(1 for r in rows if r.decision=="VERIFY"), "block": sum(1 for r in rows if r.decision=="BLOCK"), "false_positive": fp, "false_negative": fn, "accuracy": accuracy}

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    init_db()
    db = SessionLocal(); m = metrics(db); nodes = db.query(DeviceNode).order_by(DeviceNode.last_seen_at.desc()).limit(20).all(); db.close(); m["auto_running"] = SIM["running"]
    return templates.TemplateResponse("dashboard.html", {"request": request, "metrics": m, "nodes": nodes})

@app.get("/network", response_class=HTMLResponse)
def network(request: Request): return templates.TemplateResponse("network.html", {"request": request})

@app.get("/simulator", response_class=HTMLResponse)
def simulator(request: Request): return templates.TemplateResponse("simulator.html", {"request": request})

@app.get("/node", response_class=HTMLResponse)
def node_view(request: Request): return templates.TemplateResponse("node.html", {"request": request})

@app.get("/present", response_class=HTMLResponse)
def present(request: Request): return templates.TemplateResponse("present.html", {"request": request})

@app.get("/healthz")
def healthz(): return PlainTextResponse("ok")

@app.post("/create_user")
async def create_user(name: str = Form(...), email: str = Form("")):
    db = SessionLocal(); db.add(User(id=make_id("usr"), name=name.strip(), email=email.strip(), created_at=now(), last_active_at=now(), nodal_mass=10.0, status="active")); db.commit(); db.close(); await manager.broadcast({"type":"refresh"}); return RedirectResponse("/", status_code=303)

@app.post("/seed_demo_network")
async def seed_demo_network():
    db = SessionLocal()
    names = ["Manuel","Sofia","Carlos","Ana","Pedro","Lucia","Javier","Elena","Rocio","Tomas","Camila","Diego"]
    if db.query(User).count() < 8:
        for n in names:
            u = User(id=make_id("usr"), name=n, email="", created_at=now(), last_active_at=now(), nodal_mass=random.randint(8,18), status="active")
            db.add(u); db.flush()
            db.add(DeviceNode(id="node_" + uuid.uuid4().hex[:8], user_id=u.id, platform=random.choice(["mobile","web"]), created_at=now(), last_seen_at=now(), pulse_count=random.randint(1,5), cross_pulse_count=0, status="active"))
    db.commit()
    users = db.query(User).all(); ids = [u.id for u in users]
    for _ in range(min(30, max(12, len(ids)*2))):
        a, b = random.sample(ids, 2); rel = get_rel(db, a, b); rel.weight = clamp(rel.weight + random.randint(2,12), 1, 100); rel.interactions += random.randint(0,4); rel.last_interaction_at = now() - random.randint(0,60000)
    nodes = db.query(DeviceNode).all()
    for _ in range(min(12, max(4, len(nodes)))):
        a, b = random.sample(nodes, 2); write_cross_pulse(db, a.id, b.id, random.uniform(60,95), random.uniform(20,200), "seed")
    db.commit(); db.close(); await manager.broadcast({"type":"refresh"}); return RedirectResponse("/", status_code=303)

@app.post("/sim/start")
async def sim_start():
    if not SIM["running"]:
        SIM["running"] = True; SIM["task"] = asyncio.create_task(auto_loop())
    await manager.broadcast({"type":"refresh"}); return RedirectResponse("/", status_code=303)

@app.post("/sim/stop")
async def sim_stop():
    SIM["running"] = False; await manager.broadcast({"type":"refresh"}); return RedirectResponse("/", status_code=303)

@app.get("/api/users")
def api_users():
    db = SessionLocal(); out = [{"id":u.id, "name":u.name} for u in db.query(User).order_by(User.created_at.asc()).all()]; db.close(); return out

@app.get("/api/metrics")
def api_metrics():
    db = SessionLocal(); m = metrics(db); db.close(); m["auto_running"] = SIM["running"]; return m

@app.get("/api/graph")
def api_graph():
    db = SessionLocal(); data = graph_data(db); db.close(); return data

@app.get("/api/nodes")
def api_nodes():
    db = SessionLocal(); rows = db.query(DeviceNode).order_by(DeviceNode.last_seen_at.desc()).all()
    out = [{"id":r.id,"user_id":r.user_id,"platform":r.platform,"pulse_count":r.pulse_count,"cross_pulse_count":r.cross_pulse_count,"last_seen_at":r.last_seen_at} for r in rows]
    db.close(); return out

@app.get("/api/cross_pulses")
def api_cross_pulses():
    db = SessionLocal(); rows = db.query(CrossPulse).order_by(CrossPulse.created_at.desc()).limit(40).all()
    out = [{"node_a":r.node_a,"node_b":r.node_b,"shared_context_score":r.shared_context_score,"temporal_delta_ms":r.temporal_delta_ms,"source":r.source} for r in rows]
    db.close(); return out

@app.post("/api/register_node")
async def api_register_node(payload: dict):
    db = SessionLocal(); node = register_node(db, payload["node_id"], payload.get("user_id"), payload.get("platform","web")); db.commit()
    out = {"node_id":node.id,"user_id":node.user_id,"platform":node.platform,"pulse_count":node.pulse_count or 0,"cross_pulse_count":node.cross_pulse_count or 0}
    db.close(); await manager.broadcast({"type":"refresh"}); return JSONResponse(out)

@app.post("/api/pulse")
async def api_pulse(payload: dict):
    db = SessionLocal(); node = write_pulse(db, payload["node_id"], payload.get("user_id"), payload.get("platform","web")); db.commit()
    out = {"node_id":node.id,"pulse_count":node.pulse_count,"last_seen_at":node.last_seen_at}
    db.close(); await manager.broadcast({"type":"refresh"}); return JSONResponse(out)

@app.get("/api/node_status/{node_id}")
def api_node_status(node_id: str):
    db = SessionLocal(); node = get_node(db, node_id)
    if not node:
        db.close(); return JSONResponse({"error":"node not found"}, status_code=404)
    out = {"node_id":node.id,"user_id":node.user_id,"platform":node.platform,"pulse_count":node.pulse_count or 0,"cross_pulse_count":node.cross_pulse_count or 0,"last_seen_at":node.last_seen_at}
    db.close(); return out

@app.post("/api/crosspulse")
async def api_crosspulse(payload: dict):
    db = SessionLocal()
    a = payload.get("node_a"); b = payload.get("node_b")
    if not a or not b or a == b:
        db.close(); return JSONResponse({"error":"invalid nodes"}, status_code=400)
    if not get_node(db, a) or not get_node(db, b):
        db.close(); return JSONResponse({"error":"unknown node"}, status_code=400)
    write_cross_pulse(db, a, b, float(payload.get("shared_context_score",75)), float(payload.get("temporal_delta_ms",50)), payload.get("source","manual"))
    db.commit(); db.close(); await manager.broadcast({"type":"refresh"}); return JSONResponse({"ok":True,"node_a":a,"node_b":b})

@app.post("/api/evaluate")
async def api_evaluate(payload: dict):
    db = SessionLocal(); res = evaluate(db, payload, "manual", payload.get("_expected_label")); db.commit(); db.close(); await manager.broadcast({"type":"refresh"}); return JSONResponse(res)

@app.post("/api/run_scenario")
async def api_run_scenario(payload: dict):
    db = SessionLocal(); p, label = scenario_payload(db, payload.get("scenario","legit_transfer"))
    if not p:
        db.close(); return JSONResponse({"error":"not enough users"}, status_code=400)
    res = evaluate(db, p, "scenario_runner", label); db.commit(); db.close(); await manager.broadcast({"type":"refresh"}); return JSONResponse(res)

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True: await ws.receive_text()
    except WebSocketDisconnect: manager.disconnect(ws)
