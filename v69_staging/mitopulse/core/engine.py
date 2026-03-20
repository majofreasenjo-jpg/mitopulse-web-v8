
def evaluate(signal):
    if signal > 0.8:
        return "block"
    elif signal > 0.6:
        return "restrict"
    else:
        return "monitor"
