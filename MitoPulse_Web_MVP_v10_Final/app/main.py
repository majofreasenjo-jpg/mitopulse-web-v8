import os, time, uuid, math, random, asyncio
from collections import defaultdict, deque
from typing import Optional
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mitopulse_v10.db")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def now() -> int:
    return int(time.time())


def make_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def clamp(v: float, a: float, b: float) -> float:
    return max(a, min(b, v))


def decay(score: float, last_ts: Optional[int], lam: float = 0.0008) -> float:
    if not last_ts:
        return score
    return round(score * math.exp(-lam * max(0, now() - int(last_ts))), 2)


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
    created_at = Column(Integer)
    nodal_mass = Column(Float, default=10.0)
    trust_rank = Column(Float, default=20.0)
    role = Column(String, default="user")
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
    industry = Column(String)
    source = Column(String)
    expected_label = Column(String)
    decision = Column(String)
    confidence_label = Column(String)
    human_presence = Column(Float)
    freedom_score = Column(Float)
    shared_reality = Column(Float)
    situational_coherence = Column(Float)
    relational_distance_score = Column(Float)
    anchor_support_score = Column(Float)
    external_reputation_score = Column(Float)
    fraud_exposure = Column(Float)
    fraud_hunter_score = Column(Float)
    trust_score = Column(Float)
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

app = FastAPI(title="MitoPulse Web MVP v10")

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
    def __init__(self):
        self.connections = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)

    async def broadcast(self, payload: dict):
        dead = []
        for ws in self.connections:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = WSManager()
SIM = {"running": False, "tick": 0, "task": None}


SCENARIO_META = {
    "bank_transfer": {"industry": "banking", "expected": "legit"},
    "pass_transfer": {"industry": "banking", "expected": "legit"},
    "phone_scam": {"industry": "banking", "expected": "fraud"},
    "whatsapp_identity": {"industry": "social", "expected": "fraud"},
    "identity_spoof": {"industry": "social", "expected": "fraud"},
    "marketplace_sale": {"industry": "marketplace", "expected": "legit"},
    "marketplace_fraud": {"industry": "marketplace", "expected": "fraud"},
    "wallet_sign": {"industry": "crypto", "expected": "legit"},
    "wallet_drain": {"industry": "crypto", "expected": "fraud"},
}


def get_user(db, uid: str):
    return db.query(User).filter(User.id == uid).first()


def get_node(db, node_id: str):
    return db.query(DeviceNode).filter(DeviceNode.id == node_id).first()


def get_rel(db, a: str, b: str):
    rel = db.query(Relationship).filter(
        ((Relationship.user_a == a) & (Relationship.user_b == b)) |
        ((Relationship.user_a == b) & (Relationship.user_b == a))
    ).first()
    if not rel:
        rel = Relationship(
            id=make_id("rel"), user_a=a, user_b=b, weight=20.0,
            interactions=0, last_interaction_at=None, created_at=now()
        )
        db.add(rel)
        db.flush()
    return rel


def neighbors(db, uid: str):
    rels = db.query(Relationship).filter((Relationship.user_a == uid) | (Relationship.user_b == uid)).all()
    return [(r.user_b if r.user_a == uid else r.user_a, r.weight) for r in rels]


def all_risk_events_for_target(db, target_id: Optional[str]):
    if not target_id:
        return []
    return db.query(Evaluation).filter(Evaluation.target_id == target_id).all()


def human_presence(p: dict) -> float:
    duration = max(0.1, (time.time() * 1000 - int(p.get("started_at", int(time.time() * 1000)))) / 1000.0)
    clicks = int(p.get("click_count", 0))
    keys = int(p.get("key_count", 0))
    moves = int(p.get("move_count", 0))
    entropy = float(p.get("interaction_entropy", 0.2))
    hesitation = float(p.get("hesitation", 0.2))
    score = 20 + min(20, (clicks + keys) * 2.2) + min(15, moves * 0.08) + min(15, duration * 2.8) + min(20, entropy * 35) + min(10, hesitation * 20)
    return round(clamp(score, 0, 100), 2)


def freedom_score(p: dict) -> float:
    urgency = float(p.get("urgency", 0))
    dictation = float(p.get("dictation_risk", 0))
    routine = float(p.get("routine_break", 0))
    hesitation = float(p.get("hesitation", 0.2))
    return round(clamp(100 - (urgency * 30 + dictation * 35 + routine * 20 - hesitation * 8), 0, 100), 2)


def shared_reality(p: dict) -> float:
    vals = [
        float(p.get("social_overlap", 0)),
        float(p.get("temporal_alignment", 0)),
        float(p.get("context_fit", 0)),
        float(p.get("interaction_coherence", 0)),
    ]
    return round(clamp(sum(vals) * 25, 0, 100), 2)


def situational_coherence(p: dict) -> float:
    amount = float(p.get("amount", 0) or 0)
    novelty = float(p.get("transaction_novelty", 0))
    net = float(p.get("network_anomaly", 0))
    remote = float(p.get("remote_capture_probability", 0))
    amount_penalty = 25 if amount > 1500 else (15 if amount > 600 else 0)
    score = 100 - (novelty * 35 + net * 25 + remote * 20 + amount_penalty)
    return round(clamp(score, 0, 100), 2)


def relational_distance_score(db, user_id: str, target_id: Optional[str]) -> float:
    if not target_id:
        return 35.0
    if user_id == target_id:
        return 100.0
    user_ids = [u.id for u in db.query(User).all()]
    adj = defaultdict(list)
    for r in db.query(Relationship).all():
        adj[r.user_a].append(r.user_b)
        adj[r.user_b].append(r.user_a)
    dist = {user_id: 0}
    q = deque([user_id])
    while q:
        cur = q.popleft()
        if cur == target_id:
            break
        for nxt in adj[cur]:
            if nxt not in dist:
                dist[nxt] = dist[cur] + 1
                q.append(nxt)
    d = dist.get(target_id)
    if d is None:
        return 12.0 if target_id in user_ids else 8.0
    return round(clamp((1 / (1 + d)) * 100, 0, 100), 2)


def guardian_cut(users):
    masses = sorted([u.nodal_mass for u in users], reverse=True)
    if not masses:
        return 999
    return masses[max(0, min(len(masses) - 1, max(0, len(masses) // 5 - 1)))]


def guardian_ids(db):
    users = db.query(User).all()
    cut = guardian_cut(users)
    return {u.id for u in users if u.nodal_mass >= cut and len(users) >= 5}


def anchor_support_score(db, user_id: str, target_id: Optional[str]) -> float:
    gids = guardian_ids(db)
    if not gids:
        return 25.0
    support = 0.0
    seen = 0
    for uid in [user_id, target_id] if target_id else [user_id]:
        if not uid:
            continue
        for neighbor_id, weight in neighbors(db, uid):
            if neighbor_id in gids:
                g = get_user(db, neighbor_id)
                support += math.log(1 + max(g.nodal_mass, 1)) * (weight / 100)
                seen += 1
    if not seen:
        return 20.0
    return round(clamp((support / seen) * 12, 0, 100), 2)


def external_reputation_score(p: dict) -> float:
    phone = float(p.get("phone_risk", 0))
    email = float(p.get("email_leak_risk", 0))
    wallet = float(p.get("wallet_risk", 0))
    domain = float(p.get("domain_risk", 0))
    score = 100 - (phone * 30 + email * 20 + wallet * 30 + domain * 20)
    return round(clamp(score, 0, 100), 2)


def exposure_for_user(db, uid: str) -> float:
    total = 0.0
    for other_id, weight in neighbors(db, uid):
        recent = db.query(Evaluation).filter(
            ((Evaluation.user_id == other_id) | (Evaluation.target_id == other_id)) &
            (Evaluation.created_at >= now() - 86400 * 7)
        ).order_by(Evaluation.created_at.desc()).limit(12).all()
        if not recent:
            continue
        local = sum(r.fraud_hunter_score or 0 for r in recent) / len(recent)
        total += local * (weight / 100) * 0.6
    return round(clamp(total, 0, 100), 2)


def fraud_hunter_score(db, user_id: str, target_id: Optional[str], p: dict) -> float:
    subject = target_id or user_id
    subject_user = get_user(db, subject)
    rels = neighbors(db, subject)
    weak_ratio = sum(1 for _, w in rels if w < 30) / max(1, len(rels))
    expansion_velocity = clamp(float(p.get("transaction_novelty", 0)) * 100, 0, 100)
    relational_thinness = clamp(weak_ratio * 100 + (35 if len(rels) < 2 else 0), 0, 100)
    shared_deficit = 100 - shared_reality(p)
    recent_events = db.query(Evaluation).filter(
        ((Evaluation.user_id == subject) | (Evaluation.target_id == subject)) &
        (Evaluation.created_at >= now() - 86400 * 7)
    ).all()
    trigger_density = 0.0
    if recent_events:
        trigger_density = (sum(1 for e in recent_events if e.decision in ("BLOCK", "REVIEW")) / len(recent_events)) * 100
    exposure = exposure_for_user(db, subject)
    identity_volatility = 70 if subject_user and subject_user.created_at >= now() - 86400 * 14 else 20
    score = (0.20 * expansion_velocity + 0.20 * relational_thinness + 0.20 * shared_deficit + 0.15 * trigger_density + 0.15 * exposure + 0.10 * identity_volatility)
    return round(clamp(score, 0, 100), 2)


def fraud_exposure(db, user_id: str, target_id: Optional[str], p: dict) -> float:
    base = float(p.get("network_anomaly", 0)) * 35 + float(p.get("transaction_novelty", 0)) * 35 + float(p.get("remote_capture_probability", 0)) * 30
    subject = target_id or user_id
    exposure = exposure_for_user(db, subject)
    return round(clamp(base + exposure * 0.35, 0, 100), 2)


def confidence_label(trust_score: float) -> str:
    if trust_score >= 80:
        return "High Confidence"
    if trust_score >= 60:
        return "Medium Confidence"
    return "Low Confidence"


def decision_from_scores(trust_score: float, hunter: float) -> str:
    if hunter >= 80:
        return "QUARANTINE NODE"
    if trust_score >= 80:
        return "VERIFY"
    if trust_score >= 60:
        return "REVIEW"
    return "BLOCK"


def register_node(db, node_id: str, user_id: Optional[str] = None, platform: str = "web"):
    node = get_node(db, node_id)
    if not node:
        node = DeviceNode(id=node_id, user_id=user_id, platform=platform, created_at=now(), last_seen_at=now(), status="active")
        db.add(node)
    else:
        if user_id:
            node.user_id = user_id
        node.platform = platform
        node.last_seen_at = now()
        node.status = "active"
    return node


def write_pulse(db, node_id: str, user_id: Optional[str] = None, platform: str = "web"):
    node = register_node(db, node_id, user_id, platform)
    node.pulse_count = (node.pulse_count or 0) + 1
    node.last_seen_at = now()
    return node


def update_trust_rank(db):
    users = db.query(User).all()
    for user in users:
        rels = neighbors(db, user.id)
        if rels:
            support = sum(weight for _, weight in rels) / len(rels)
        else:
            support = 10
        user.trust_rank = round(clamp(0.6 * user.nodal_mass + 0.4 * support, 1, 100), 2)


def write_cross_pulse(db, node_a: str, node_b: str, shared_score: float, temporal_delta_ms: float = 0.0, source: str = "manual"):
    db.add(CrossPulse(
        id=make_id("xp"), node_a=node_a, node_b=node_b,
        shared_context_score=round(shared_score, 2), temporal_delta_ms=round(temporal_delta_ms, 2),
        source=source, created_at=now()
    ))
    na, nb = get_node(db, node_a), get_node(db, node_b)
    if na:
        na.cross_pulse_count = (na.cross_pulse_count or 0) + 1
    if nb:
        nb.cross_pulse_count = (nb.cross_pulse_count or 0) + 1
    if na and nb and na.user_id and nb.user_id and na.user_id != nb.user_id and get_user(db, na.user_id) and get_user(db, nb.user_id):
        rel = get_rel(db, na.user_id, nb.user_id)
        rel.interactions += 1
        rel.last_interaction_at = now()
        rel.weight = round(clamp(rel.weight + max(0.5, shared_score / 20.0), 1, 100), 2)
        update_trust_rank(db)


def evaluate(db, p: dict, source: str = "manual", expected_label: Optional[str] = None) -> dict:
    meta = SCENARIO_META.get(p.get("scenario", "bank_transfer"), {"industry": "generic", "expected": expected_label})
    expected = expected_label or meta.get("expected")
    hp = human_presence(p)
    freedom = freedom_score(p)
    sr = shared_reality(p)
    situ = situational_coherence(p)
    rds = relational_distance_score(db, p["user_id"], p.get("target_id"))
    anchor = anchor_support_score(db, p["user_id"], p.get("target_id"))
    external = external_reputation_score(p)
    hunter = fraud_hunter_score(db, p["user_id"], p.get("target_id"), p)
    exposure = fraud_exposure(db, p["user_id"], p.get("target_id"), p)
    trust_score = round(clamp(0.15 * hp + 0.15 * freedom + 0.18 * sr + 0.17 * situ + 0.15 * rds + 0.10 * anchor + 0.10 * external - 0.25 * exposure, 0, 100), 2)
    decision = decision_from_scores(trust_score, hunter)
    guardian_alert = 1 if p.get("scenario") in ("phone_scam", "whatsapp_identity", "identity_spoof", "wallet_drain", "marketplace_fraud") and (freedom < 45 or sr < 40 or rds < 35) else 0
    conf = confidence_label(trust_score)
    row = Evaluation(
        id=make_id("eval"), event_id=make_id("evt"), user_id=p["user_id"], target_id=p.get("target_id"),
        scenario=p.get("scenario", "bank_transfer"), industry=meta.get("industry", "generic"), source=source,
        expected_label=expected, decision=decision, confidence_label=conf,
        human_presence=hp, freedom_score=freedom, shared_reality=sr, situational_coherence=situ,
        relational_distance_score=rds, anchor_support_score=anchor, external_reputation_score=external,
        fraud_exposure=exposure, fraud_hunter_score=hunter, trust_score=trust_score,
        guardian_alert=guardian_alert, created_at=now()
    )
    db.add(row)
    u = get_user(db, p["user_id"])
    if u:
        u.last_active_at = now()
        u.nodal_mass = clamp(u.nodal_mass + (2 if decision == "VERIFY" else (-1.2 if decision in ("BLOCK", "QUARANTINE NODE") else 0.2)), 1, 100)
    if p.get("target_id") and get_user(db, p["target_id"]):
        t = get_user(db, p["target_id"])
        t.last_active_at = now()
        t.nodal_mass = clamp(t.nodal_mass + (0.6 if decision == "VERIFY" else (-0.5 if decision in ("BLOCK", "QUARANTINE NODE") else 0.1)), 1, 100)
        rel = get_rel(db, p["user_id"], p["target_id"])
        rel.interactions += 1
        rel.last_interaction_at = now()
        rel.weight = round(clamp(rel.weight + (4 if decision == "VERIFY" else (-2 if decision in ("BLOCK", "QUARANTINE NODE") else 0.5)), 1, 100), 2)
    update_trust_rank(db)
    return {
        "decision": decision,
        "confidence_label": conf,
        "guardian_alert": guardian_alert,
        "trust_score": trust_score,
        "human_presence": hp,
        "freedom_score": freedom,
        "shared_reality": sr,
        "situational_coherence": situ,
        "relational_distance_score": rds,
        "anchor_support_score": anchor,
        "external_reputation_score": external,
        "fraud_exposure": exposure,
        "fraud_hunter_score": hunter,
        "industry": meta.get("industry", "generic")
    }


def scenario_payload(db, scenario: str):
    users = db.query(User).all()
    if len(users) < 2:
        return None, None
    user, target = random.sample(users, 2)
    presets = {
        "bank_transfer": dict(amount=160, urgency=.2, dictation_risk=.0, routine_break=.1, social_overlap=.8, temporal_alignment=.8, context_fit=.8, interaction_coherence=.8, network_anomaly=.1, transaction_novelty=.2, remote_capture_probability=.0, phone_risk=.0, email_leak_risk=.0, wallet_risk=.0, domain_risk=.0),
        "pass_transfer": dict(amount=280, urgency=.1, dictation_risk=.0, routine_break=.1, social_overlap=.7, temporal_alignment=.7, context_fit=.8, interaction_coherence=.8, network_anomaly=.1, transaction_novelty=.3, remote_capture_probability=.0, phone_risk=.0, email_leak_risk=.0, wallet_risk=.0, domain_risk=.0),
        "phone_scam": dict(amount=1400, urgency=.95, dictation_risk=.9, routine_break=.85, social_overlap=.1, temporal_alignment=.2, context_fit=.15, interaction_coherence=.25, network_anomaly=.7, transaction_novelty=.9, remote_capture_probability=.8, phone_risk=.8, email_leak_risk=.2, wallet_risk=.0, domain_risk=.1),
        "whatsapp_identity": dict(amount=950, urgency=.9, dictation_risk=.7, routine_break=.8, social_overlap=.15, temporal_alignment=.25, context_fit=.2, interaction_coherence=.25, network_anomaly=.6, transaction_novelty=.85, remote_capture_probability=.7, phone_risk=.7, email_leak_risk=.1, wallet_risk=.0, domain_risk=.0),
        "identity_spoof": dict(amount=650, urgency=.75, dictation_risk=.6, routine_break=.7, social_overlap=.2, temporal_alignment=.3, context_fit=.2, interaction_coherence=.3, network_anomaly=.65, transaction_novelty=.75, remote_capture_probability=.65, phone_risk=.6, email_leak_risk=.2, wallet_risk=.0, domain_risk=.2),
        "marketplace_sale": dict(amount=120, urgency=.1, dictation_risk=.0, routine_break=.2, social_overlap=.35, temporal_alignment=.6, context_fit=.65, interaction_coherence=.7, network_anomaly=.2, transaction_novelty=.4, remote_capture_probability=.1, phone_risk=.0, email_leak_risk=.0, wallet_risk=.0, domain_risk=.0),
        "marketplace_fraud": dict(amount=520, urgency=.8, dictation_risk=.2, routine_break=.7, social_overlap=.05, temporal_alignment=.35, context_fit=.2, interaction_coherence=.25, network_anomaly=.75, transaction_novelty=.95, remote_capture_probability=.45, phone_risk=.1, email_leak_risk=.0, wallet_risk=.0, domain_risk=.8),
        "wallet_sign": dict(amount=180, urgency=.1, dictation_risk=.0, routine_break=.1, social_overlap=.3, temporal_alignment=.7, context_fit=.75, interaction_coherence=.75, network_anomaly=.15, transaction_novelty=.3, remote_capture_probability=.15, phone_risk=.0, email_leak_risk=.0, wallet_risk=.1, domain_risk=.1),
        "wallet_drain": dict(amount=2400, urgency=.92, dictation_risk=.55, routine_break=.9, social_overlap=.0, temporal_alignment=.2, context_fit=.1, interaction_coherence=.2, network_anomaly=.85, transaction_novelty=.95, remote_capture_probability=.75, phone_risk=.0, email_leak_risk=.1, wallet_risk=.9, domain_risk=.85),
    }
    base = presets.get(scenario, presets["bank_transfer"])
    payload = {
        "user_id": user.id,
        "target_id": target.id,
        "scenario": scenario,
        "started_at": int(time.time() * 1000) - random.randint(1000, 12000),
        "click_count": random.randint(2, 15),
        "key_count": random.randint(1, 10),
        "move_count": random.randint(12, 120),
        "interaction_entropy": round(random.uniform(0.18, 0.92), 2),
        "hesitation": round(random.uniform(0.15, 0.75), 2),
    }
    payload.update(base)
    return payload, SCENARIO_META.get(scenario, {}).get("expected")


def metrics(db):
    rows = db.query(Evaluation).all()
    legit = [r for r in rows if r.expected_label == "legit"]
    fraud = [r for r in rows if r.expected_label == "fraud"]
    false_positive = sum(1 for r in legit if r.decision in ("BLOCK", "QUARANTINE NODE"))
    false_negative = sum(1 for r in fraud if r.decision == "VERIFY")
    legit_ok = sum(1 for r in legit if r.decision not in ("BLOCK", "QUARANTINE NODE"))
    fraud_ok = sum(1 for r in fraud if r.decision != "VERIFY")
    total_eval = len(legit) + len(fraud)
    accuracy = round(((legit_ok + fraud_ok) / total_eval) * 100, 2) if total_eval else 0
    by_industry = defaultdict(int)
    for r in rows:
        by_industry[r.industry] += 1
    return {
        "users": db.query(User).count(),
        "nodes": db.query(DeviceNode).count(),
        "relationships": db.query(Relationship).count(),
        "cross_pulses": db.query(CrossPulse).count(),
        "verify": sum(1 for r in rows if r.decision == "VERIFY"),
        "review": sum(1 for r in rows if r.decision == "REVIEW"),
        "block": sum(1 for r in rows if r.decision == "BLOCK"),
        "quarantine": sum(1 for r in rows if r.decision == "QUARANTINE NODE"),
        "false_positive": false_positive,
        "false_negative": false_negative,
        "accuracy": accuracy,
        "banking_events": by_industry["banking"],
        "marketplace_events": by_industry["marketplace"],
        "crypto_events": by_industry["crypto"],
        "social_events": by_industry["social"],
    }


def graph_data(db):
    users = db.query(User).all()
    rels = db.query(Relationship).all()
    adj = defaultdict(list)
    for r in rels:
        adj[r.user_a].append(r.user_b)
        adj[r.user_b].append(r.user_a)
    comp, cid = {}, 0
    for u in users:
        if u.id in comp:
            continue
        cid += 1
        q = deque([u.id])
        comp[u.id] = cid
        while q:
            cur = q.popleft()
            for nxt in adj[cur]:
                if nxt not in comp:
                    comp[nxt] = cid
                    q.append(nxt)
    gids = guardian_ids(db)
    last_eval = {}
    for e in db.query(Evaluation).order_by(Evaluation.created_at.desc()).all():
        if e.user_id not in last_eval:
            last_eval[e.user_id] = e
    nodes = []
    for u in users:
        state = "healthy"
        color_hint = 0
        ev = last_eval.get(u.id)
        if ev:
            if (ev.fraud_hunter_score or 0) >= 80 or ev.decision == "QUARANTINE NODE":
                state = "quarantined"; color_hint = 3
            elif (ev.fraud_hunter_score or 0) >= 60:
                state = "high_risk"; color_hint = 2
            elif (ev.fraud_hunter_score or 0) >= 35:
                state = "monitored"; color_hint = 1
        nodes.append({
            "id": u.id, "label": u.name, "mass": round(u.nodal_mass, 2), "trust_rank": round(u.trust_rank or 0, 2),
            "cluster": comp.get(u.id, 0), "guardian": u.id in gids, "state": state, "color_hint": color_hint,
        })
    links = [{"source": r.user_a, "target": r.user_b, "weight": round(r.weight, 2)} for r in rels]
    return {"nodes": nodes, "links": links}


def suspicious_nodes(db):
    latest = {}
    for e in db.query(Evaluation).order_by(Evaluation.created_at.desc()).limit(200).all():
        subject = e.target_id or e.user_id
        if subject not in latest:
            latest[subject] = e
    rows = []
    for subject, e in latest.items():
        user = get_user(db, subject)
        rows.append({
            "user_id": subject,
            "name": user.name if user else subject,
            "fraud_hunter_score": round(e.fraud_hunter_score or 0, 2),
            "decision": e.decision,
            "scenario": e.scenario,
            "state": "quarantined" if (e.fraud_hunter_score or 0) >= 80 or e.decision == "QUARANTINE NODE" else ("high_risk" if (e.fraud_hunter_score or 0) >= 60 else ("monitored" if (e.fraud_hunter_score or 0) >= 35 else "healthy"))
        })
    rows.sort(key=lambda x: x["fraud_hunter_score"], reverse=True)
    return rows[:20]


async def auto_loop():
    scenarios = list(SCENARIO_META.keys())
    while SIM["running"]:
        db = SessionLocal()
        try:
            mode = random.choices(["scenario", "crosspulse", "pulse"], weights=[5, 2, 2], k=1)[0]
            if mode == "scenario":
                scenario = random.choice(scenarios)
                p, label = scenario_payload(db, scenario)
                if p:
                    evaluate(db, p, "auto_demo", label)
            elif mode == "crosspulse":
                nodes = db.query(DeviceNode).all()
                if len(nodes) >= 2:
                    a, b = random.sample(nodes, 2)
                    write_cross_pulse(db, a.id, b.id, random.uniform(60, 95), random.uniform(20, 250), "auto_demo")
            else:
                nodes = db.query(DeviceNode).all()
                if nodes:
                    n = random.choice(nodes)
                    write_pulse(db, n.id, n.user_id, n.platform)
            db.commit()
            SIM["tick"] += 1
        finally:
            db.close()
        await manager.broadcast({"type": "refresh", "tick": SIM["tick"]})
        await asyncio.sleep(2.0)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    init_db()
    db = SessionLocal()
    m = metrics(db)
    nodes = db.query(DeviceNode).order_by(DeviceNode.last_seen_at.desc()).limit(20).all()
    threats = suspicious_nodes(db)
    db.close()
    m["auto_running"] = SIM["running"]
    return templates.TemplateResponse("dashboard.html", {"request": request, "metrics": m, "nodes": nodes, "threats": threats})


@app.get("/network", response_class=HTMLResponse)
def network(request: Request):
    return templates.TemplateResponse("network.html", {"request": request})


@app.get("/simulator", response_class=HTMLResponse)
def simulator(request: Request):
    return templates.TemplateResponse("simulator.html", {"request": request, "scenarios": list(SCENARIO_META.keys())})


@app.get("/node", response_class=HTMLResponse)
def node_view(request: Request):
    return templates.TemplateResponse("node.html", {"request": request})


@app.get("/present", response_class=HTMLResponse)
def present(request: Request):
    return templates.TemplateResponse("present.html", {"request": request})


@app.get("/healthz")
def healthz():
    return PlainTextResponse("ok")


@app.post("/create_user")
async def create_user(name: str = Form(...), email: str = Form("")):
    db = SessionLocal()
    db.add(User(id=make_id("usr"), name=name.strip(), email=email.strip(), created_at=now(), last_active_at=now(), nodal_mass=10.0, trust_rank=20.0, status="active", role="user"))
    db.commit()
    db.close()
    await manager.broadcast({"type": "refresh"})
    return RedirectResponse("/", status_code=303)


@app.post("/seed_demo_network")
async def seed_demo_network():
    db = SessionLocal()
    names = ["Manuel", "Sofia", "Carlos", "Ana", "Pedro", "Lucia", "Javier", "Elena", "Rocio", "Tomas", "Camila", "Diego"]
    if db.query(User).count() < 10:
        for idx, name in enumerate(names):
            role = "guardian" if idx in (0, 1) else "user"
            mass = random.randint(18, 28) if role == "guardian" else random.randint(8, 16)
            u = User(id=make_id("usr"), name=name, email="", created_at=now() - random.randint(0, 86400 * 40), last_active_at=now(), nodal_mass=mass, trust_rank=mass, role=role, status="active")
            db.add(u)
            db.flush()
            db.add(DeviceNode(id="node_" + uuid.uuid4().hex[:8], user_id=u.id, platform=random.choice(["mobile", "web"]), created_at=now(), last_seen_at=now(), pulse_count=random.randint(1, 5), cross_pulse_count=0, status="active"))
        db.commit()
    users = db.query(User).all()
    ids = [u.id for u in users]
    for _ in range(min(36, max(14, len(ids) * 3))):
        a, b = random.sample(ids, 2)
        rel = get_rel(db, a, b)
        rel.weight = clamp(rel.weight + random.randint(2, 16), 1, 100)
        rel.interactions += random.randint(0, 6)
        rel.last_interaction_at = now() - random.randint(0, 86400 * 20)
    update_trust_rank(db)
    nodes = db.query(DeviceNode).all()
    for _ in range(min(18, max(6, len(nodes)))):
        a, b = random.sample(nodes, 2)
        write_cross_pulse(db, a.id, b.id, random.uniform(60, 95), random.uniform(20, 200), "seed")
    for _ in range(24):
        scenario = random.choice(list(SCENARIO_META.keys()))
        p, label = scenario_payload(db, scenario)
        if p:
            evaluate(db, p, "seed", label)
    db.commit()
    db.close()
    await manager.broadcast({"type": "refresh"})
    return RedirectResponse("/", status_code=303)


@app.post("/sim/start")
async def sim_start():
    if not SIM["running"]:
        SIM["running"] = True
        SIM["task"] = asyncio.create_task(auto_loop())
    await manager.broadcast({"type": "refresh"})
    return RedirectResponse("/", status_code=303)


@app.post("/sim/stop")
async def sim_stop():
    SIM["running"] = False
    await manager.broadcast({"type": "refresh"})
    return RedirectResponse("/", status_code=303)


@app.get("/api/users")
def api_users():
    db = SessionLocal()
    out = [{"id": u.id, "name": u.name, "role": u.role} for u in db.query(User).order_by(User.created_at.asc()).all()]
    db.close()
    return out


@app.get("/api/metrics")
def api_metrics():
    init_db()
    db = SessionLocal()
    out = metrics(db)
    db.close()
    out["auto_running"] = SIM["running"]
    return out


@app.get("/api/graph")
def api_graph():
    db = SessionLocal()
    out = graph_data(db)
    db.close()
    return out


@app.get("/api/nodes")
def api_nodes():
    db = SessionLocal()
    rows = db.query(DeviceNode).order_by(DeviceNode.last_seen_at.desc()).all()
    out = [{"id": r.id, "user_id": r.user_id, "platform": r.platform, "pulse_count": r.pulse_count, "cross_pulse_count": r.cross_pulse_count, "last_seen_at": r.last_seen_at} for r in rows]
    db.close()
    return out


@app.get("/api/cross_pulses")
def api_cross_pulses():
    db = SessionLocal()
    rows = db.query(CrossPulse).order_by(CrossPulse.created_at.desc()).limit(50).all()
    out = [{"node_a": r.node_a, "node_b": r.node_b, "shared_context_score": r.shared_context_score, "temporal_delta_ms": r.temporal_delta_ms, "source": r.source} for r in rows]
    db.close()
    return out


@app.get("/api/threats")
def api_threats():
    db = SessionLocal()
    out = suspicious_nodes(db)
    db.close()
    return out


@app.get("/api/recent_evaluations")
def api_recent_evaluations():
    db = SessionLocal()
    rows = db.query(Evaluation).order_by(Evaluation.created_at.desc()).limit(40).all()
    out = [{
        "scenario": r.scenario, "industry": r.industry, "decision": r.decision, "confidence_label": r.confidence_label,
        "trust_score": r.trust_score, "fraud_hunter_score": r.fraud_hunter_score, "guardian_alert": r.guardian_alert,
        "expected_label": r.expected_label, "created_at": r.created_at
    } for r in rows]
    db.close()
    return out


@app.post("/api/register_node")
async def api_register_node(payload: dict):
    db = SessionLocal()
    node = register_node(db, payload["node_id"], payload.get("user_id"), payload.get("platform", "web"))
    db.commit()
    out = {"node_id": node.id, "user_id": node.user_id, "platform": node.platform, "pulse_count": node.pulse_count or 0, "cross_pulse_count": node.cross_pulse_count or 0}
    db.close()
    await manager.broadcast({"type": "refresh"})
    return JSONResponse(out)


@app.post("/api/pulse")
async def api_pulse(payload: dict):
    db = SessionLocal()
    node = write_pulse(db, payload["node_id"], payload.get("user_id"), payload.get("platform", "web"))
    db.commit()
    out = {"node_id": node.id, "pulse_count": node.pulse_count, "last_seen_at": node.last_seen_at}
    db.close()
    await manager.broadcast({"type": "refresh"})
    return JSONResponse(out)


@app.get("/api/node_status/{node_id}")
def api_node_status(node_id: str):
    db = SessionLocal()
    node = get_node(db, node_id)
    if not node:
        db.close()
        return JSONResponse({"error": "node not found"}, status_code=404)
    out = {"node_id": node.id, "user_id": node.user_id, "platform": node.platform, "pulse_count": node.pulse_count or 0, "cross_pulse_count": node.cross_pulse_count or 0, "last_seen_at": node.last_seen_at}
    db.close()
    return out


@app.post("/api/crosspulse")
async def api_crosspulse(payload: dict):
    db = SessionLocal()
    a = payload.get("node_a")
    b = payload.get("node_b")
    if not a or not b or a == b:
        db.close()
        return JSONResponse({"error": "invalid nodes"}, status_code=400)
    if not get_node(db, a) or not get_node(db, b):
        db.close()
        return JSONResponse({"error": "unknown node"}, status_code=400)
    write_cross_pulse(db, a, b, float(payload.get("shared_context_score", 75)), float(payload.get("temporal_delta_ms", 50)), payload.get("source", "manual"))
    db.commit()
    db.close()
    await manager.broadcast({"type": "refresh"})
    return JSONResponse({"ok": True, "node_a": a, "node_b": b})


@app.post("/api/evaluate")
async def api_evaluate(payload: dict):
    db = SessionLocal()
    res = evaluate(db, payload, payload.get("source", "manual"), payload.get("_expected_label"))
    db.commit()
    db.close()
    await manager.broadcast({"type": "refresh"})
    return JSONResponse(res)


@app.post("/api/run_scenario")
async def api_run_scenario(payload: dict):
    db = SessionLocal()
    p, label = scenario_payload(db, payload.get("scenario", "bank_transfer"))
    if not p:
        db.close()
        return JSONResponse({"error": "not enough users"}, status_code=400)
    res = evaluate(db, p, "scenario_runner", label)
    db.commit()
    db.close()
    await manager.broadcast({"type": "refresh"})
    return JSONResponse(res)


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
