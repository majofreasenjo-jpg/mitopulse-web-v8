from __future__ import annotations

def score_signal(ticker: dict) -> dict:
    change = abs(float(ticker.get("price_change_percent", 0.0)))
    volume = float(ticker.get("quote_volume", 0.0))
    signal = min(0.99, 0.25 + change / 8.0 + (0.15 if volume > 5e8 else 0.0))
    decision = "approve"
    if signal >= 0.85:
        decision = "block"
    elif signal >= 0.65:
        decision = "restrict"
    elif signal >= 0.45:
        decision = "monitor"
    return {
        "signal": round(signal, 4),
        "decision": decision,
        "confidence": round(min(0.99, 0.70 + signal * 0.25), 4),
    }

def impact_report(ticker: dict, analysis: dict) -> dict:
    base_exposure = 100000
    prevented = base_exposure * analysis["signal"]
    roi = (prevented - 20000) / 20000
    return {
        "prevented_usd": round(prevented, 2),
        "roi": round(roi, 4),
        "executive_summary": f"MitoPulse recomienda {analysis['decision']} con confianza {analysis['confidence']} y ahorro potencial de ${round(prevented, 2)}"
    }

def build_story(ticker: dict, analysis: dict, impact: dict) -> dict:
    state = "stable"
    if analysis["signal"] >= 0.85:
        state = "critical"
    elif analysis["signal"] >= 0.65:
        state = "pressure"
    elif analysis["signal"] >= 0.45:
        state = "watch"
    return {
        "title": f"MitoPulse detected {state} conditions on {ticker['symbol']}",
        "narrative": f"Price changed {ticker['price_change_percent']}% in the last 24h. The protocol classified the asset as {state}, recommended {analysis['decision']}, and estimated ${impact['prevented_usd']} in potential protected value.",
        "state": state
    }
