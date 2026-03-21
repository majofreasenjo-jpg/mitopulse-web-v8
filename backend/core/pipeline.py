from backend.modules.propagation import propagate
from backend.modules.benchmark import benchmark
from backend.modules.trust import trust_score
from backend.modules.federation import quorum
from backend.modules.impact import impact_calc

def run_pipeline(signal: float):
    """
    True Orchestrated Pipeline V72
    data -> propagation -> decision -> trust -> federation -> action -> impact -> visual
    """
    
    # 1. Feed signal to Risk Propagation Layer
    p = propagate(signal)
    
    # 2. Benchmark the Propagation against traditional algorithms
    b = benchmark(signal, p)
    
    # 3. Derive Trust Degradation caused by the propagation
    t = trust_score(p)
    
    # 4. Solicit a Network Quorum (Federation Layer) based on Trust and Risk
    q = quorum(t, p)
    
    # 5. Calculate Financial Action / Impact based on Federation consensus
    i = impact_calc(q, b)
    
    # 6. Global Autonomous Decision (Action Engine equivalent)
    decision = "block" if q.get("consensus_score", 0.0) >= 0.70 else "monitor"
    
    return {
        "pipeline_version": "v72.0.0-PROD",
        "signal_ingested": signal,
        "propagation": p,
        "benchmark": b,
        "trust": t,
        "federation": q,
        "impact": i,
        "final_decision": decision
    }
