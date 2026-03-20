
def compute_trust(confidence, stability):
    return round((confidence * 0.7 + stability * 0.3), 4)
