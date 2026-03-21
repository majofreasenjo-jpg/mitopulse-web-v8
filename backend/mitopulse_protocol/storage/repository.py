from mitopulse_protocol.storage.db import get_conn

def insert_event(event_id, event_type, entity_id, payload_json, ts):
    conn = get_conn()
    conn.execute("INSERT INTO events(event_id,event_type,entity_id,payload_json,ts) VALUES (?,?,?,?,?)",
                 (event_id, event_type, entity_id, payload_json, ts))
    conn.commit()
    conn.close()

def save_evaluation(entity_id, identity_state, trust_state, risk_state, scr, validated, action_type, recovery_state):
    conn = get_conn()
    conn.execute(
        "INSERT INTO evaluations(entity_id,identity_state,trust_state,risk_state,scr,validated,action_type,recovery_state) VALUES (?,?,?,?,?,?,?,?)",
        (entity_id, identity_state, trust_state, risk_state, scr, validated, action_type, recovery_state)
    )
    eid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    conn.close()
    return eid

def add_vote(evaluation_id, vote_id, anchor_id, confidence, vote, ts):
    conn = get_conn()
    conn.execute("INSERT INTO votes(vote_id,evaluation_id,anchor_id,confidence,vote,ts) VALUES (?,?,?,?,?,?)",
                 (vote_id, evaluation_id, anchor_id, confidence, vote, ts))
    conn.commit()
    conn.close()

def add_challenge(challenge_id, evaluation_id, reason, status, ts):
    conn = get_conn()
    conn.execute("INSERT INTO challenges(challenge_id,evaluation_id,reason,status,ts) VALUES (?,?,?,?,?)",
                 (challenge_id, evaluation_id, reason, status, ts))
    conn.commit()
    conn.close()

def update_action_approval(action_id, approved):
    conn = get_conn()
    conn.execute("UPDATE actions SET approved = ? WHERE action_id = ?", (approved, action_id))
    conn.commit()
    conn.close()

def insert_action(action_id, evaluation_id, target_id, action_type, approved, explanation, policy_id, ts):
    conn = get_conn()
    conn.execute("INSERT INTO actions(action_id,evaluation_id,target_id,action_type,approved,explanation,policy_id,ts) VALUES (?,?,?,?,?,?,?,?)",
                 (action_id, evaluation_id, target_id, action_type, approved, explanation, policy_id, ts))
    conn.commit()
    conn.close()

def list_rows(table, limit=100):
    conn = get_conn()
    rows = [dict(r) for r in conn.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]
    conn.close()
    return rows

def list_policies():
    conn = get_conn()
    rows = [dict(r) for r in conn.execute("SELECT * FROM policies ORDER BY policy_id").fetchall()]
    conn.close()
    return rows

def create_policy(payload):
    conn = get_conn()
    conn.execute(
        "INSERT INTO policies(policy_id,name,condition_text,action_text,confidence_required,quorum_required,severity_band,enabled,version,explanation) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            payload["policy_id"], payload["name"], payload["condition_text"], payload["action_text"],
            payload["confidence_required"], payload["quorum_required"], payload["severity_band"],
            payload.get("enabled",1), payload.get("version",1), payload["explanation"]
        )
    )
    conn.commit()
    conn.close()

def toggle_policy(policy_id, enabled):
    conn = get_conn()
    conn.execute("UPDATE policies SET enabled = ? WHERE policy_id = ?", (enabled, policy_id))
    conn.commit()
    conn.close()

def list_events(limit=500): return list_rows("events", limit)
def list_evaluations(limit=200): return list_rows("evaluations", limit)
def list_votes(limit=300): return list_rows("votes", limit)
def list_challenges(limit=300): return list_rows("challenges", limit)
def list_actions(limit=300): return list_rows("actions", limit)
def list_anchors(limit=100): return list_rows("federation_anchors", limit)
def list_exchanges(limit=300): return list_rows("federation_exchanges", limit)
def list_entities(limit=500): return list_rows("entities", limit)
def list_trust_profiles(limit=500): return list_rows("trust_profiles", limit)
def list_users(limit=500): return list_rows("users", limit)
def list_tenants(limit=50): return list_rows("tenants", limit)
