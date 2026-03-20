
from mitopulse.modules.trust import trust_score
from mitopulse.modules.federation import quorum
from mitopulse.modules.impact import calculate_impact_map

def evaluate(signal):
    decision = "block" if signal > 0.8 else ("restrict" if signal > 0.6 else "monitor")
    
    simulated_votes = [signal, signal*0.9, signal*1.1, signal*0.95]
    
    return {
        "decision": decision,
        "base_signal": signal,
        "trust_layer": trust_score(signal),
        "federation_quorum": quorum(simulated_votes),
        "propagation_impact": calculate_impact_map(signal)
    }
