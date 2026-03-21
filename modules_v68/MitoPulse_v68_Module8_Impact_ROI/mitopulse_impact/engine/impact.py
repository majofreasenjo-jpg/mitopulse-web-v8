
def loss_prevented(events):
    return sum(e["amount"] * e["probability"] for e in events)

def roi(saved, cost):
    return (saved - cost) / cost if cost else 0

def efficiency_gain(baseline_loss, mito_loss):
    return (baseline_loss - mito_loss) / baseline_loss if baseline_loss else 0
