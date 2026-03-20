def quorum_activation(signal_values, weights, theta=0.9):
    total = 0.0
    details = []
    for s, w in zip(signal_values, weights):
        contrib = float(s) * float(w)
        total += contrib
        details.append(round(contrib, 3))
    return {"quorum_score": round(total, 3), "activated": total >= theta, "theta": theta, "contributions": details}
