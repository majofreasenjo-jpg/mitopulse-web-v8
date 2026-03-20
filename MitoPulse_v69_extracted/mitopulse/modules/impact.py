
def loss_prevented(events):
    return sum(e.get("amount", 0) * e.get("prob", 0) for e in events)

def calculate_impact_map(base_signal):
    assets = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
    return {asset: round(base_signal * (0.85 ** i), 4) for i, asset in enumerate(assets)}
