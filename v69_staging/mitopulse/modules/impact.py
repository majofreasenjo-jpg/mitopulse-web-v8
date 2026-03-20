
def loss_prevented(events):
    return sum(e["amount"]*e["prob"] for e in events)
