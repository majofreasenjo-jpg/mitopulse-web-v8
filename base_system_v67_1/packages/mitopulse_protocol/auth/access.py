ROLES = {
    "admin": ["view", "evaluate", "approve", "manage_policies", "manage_federation"],
    "operator": ["view", "evaluate"],
    "auditor": ["view"]
}
def can(role: str, permission: str) -> bool:
    return permission in ROLES.get(role, [])
