from __future__ import annotations
import random
import time

def get_tradfi_metrics(symbols: list[str] = ["SPY", "QQQ", "^VIX", "GC=F", "^TNX"]) -> list[dict]:
    """
    V87 Omniverse Traditional Finance (TradFi) Ingestion Module.
    Simulates hyper-realistic market correlations (e.g. VIX spikes when SPY drops)
    to feed exactly into the same `signals_data` schema expected by the RFDC Engine.
    """
    out = []
    
    # Base correlations using mathematical pseudo-random walks based on timestamp
    tick = int(time.time() / 10) # 10-second momentum
    
    spy_base = 520.0
    qqq_base = 445.0
    vix_base = 14.50
    gc_base = 2300.0
    tnx_base = 4.30
    
    vix_spike = random.uniform(-0.5, 2.5) if (tick % 7 == 0) else random.uniform(-0.2, 0.2)
    # Inverse correlation: If VIX spikes, SPY/QQQ drop
    market_momentum = -vix_spike * 1.5 + random.uniform(-0.1, 0.2)
    
    assets = {
        "SPY": (spy_base + (market_momentum * 10.0), market_momentum / spy_base * 100),
        "QQQ": (qqq_base + (market_momentum * 12.0), market_momentum / qqq_base * 100),
        "^VIX": (vix_base + vix_spike, vix_spike / vix_base * 100),
        "GC=F": (gc_base + (random.uniform(-5.0, 5.0)), random.uniform(-0.3, 0.3)), # Gold is somewhat decoupled
        "^TNX": (tnx_base + (random.uniform(-0.05, 0.05)), random.uniform(-1.0, 1.0))
    }
    
    for s in symbols:
        if s in assets:
            price, pct = assets[s]
            out.append({
                "symbol": s,
                "last_price": round(price, 2),
                "price_change_percent": round(pct, 2),
                "quote_volume": random.uniform(10_000_000, 50_000_000), # TradFi volume
                "high_price": round(price * 1.01, 2),
                "low_price": round(price * 0.99, 2),
                "open_price": round(price, 2),
                "count": int(random.uniform(5000, 20000)),
            })
        else:
            out.append({"symbol": s, "error": "TRADFI_NOT_FOUND"})
            
    return out
