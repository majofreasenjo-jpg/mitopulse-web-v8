from mitopulse_protocol.models.objects import PolicyObject
from mitopulse_protocol.storage.repository import list_policies

def load_policies():
    rows = list_policies()
    out = []
    for r in rows:
        if int(r.get("enabled", 1)) != 1:
            continue
        out.append(PolicyObject(
            policy_id=r["policy_id"],
            name=r["name"],
            condition_text=r["condition_text"],
            action_text=r["action_text"],
            confidence_required=float(r["confidence_required"]),
            quorum_required=float(r["quorum_required"]),
            severity_band=r["severity_band"],
            enabled=int(r["enabled"]),
            version=int(r["version"]),
            explanation=r["explanation"],
        ))
    return out

def select_policy(scr: float):
    policies = load_policies()
    # choose by action severity ordering derived from score
    candidates = []
    for p in policies:
        cond = p.condition_text.replace("scr", str(scr))
        try:
            if eval(cond):
                candidates.append(p)
        except Exception:
            pass
    if not candidates:
        return None
    # highest threshold wins by confidence/quorum sum
    candidates.sort(key=lambda x: (x.confidence_required + x.quorum_required, x.version), reverse=True)
    return candidates[0]
