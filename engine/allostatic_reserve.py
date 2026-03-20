def allostatic_trust_reserve(base_trust, recovery, stress):
    reserve = max(0.0, min(1.0, float(base_trust) + float(recovery) - float(stress)))
    return round(reserve, 3)

def reserve_components(relational_identity, danger_score, reality_anchor=0.10):
    recovery = min(0.35, relational_identity * 0.25 + reality_anchor)
    stress = min(0.60, danger_score * 0.55)
    reserve = allostatic_trust_reserve(relational_identity, recovery, stress)
    return {"recovery_component": round(recovery, 3), "stress_component": round(stress, 3), "allostatic_reserve": reserve}
