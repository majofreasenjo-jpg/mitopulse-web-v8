
def build_explanation(signal, propagation):
    return {
        "drivers": ["volatility_spike", "volume_anomaly"],
        "propagation_path": propagation,
        "confidence": round(0.8 + abs(signal)*0.1, 4)
    }
