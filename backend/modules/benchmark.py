def benchmark(signal: float, propagation_data: dict):
    # Compare Traditional Systems vs MitoPulse Protocol Capability
    mp_score = propagation_data.get("scr", 0)
    
    # A naive traditional system responds linearly to signals and maxes out early
    traditional_score = min(100.0, signal * 35.0) 
    
    # Calculate the exact advantage (alpha generation capability) in mitigation
    advantage = round(mp_score - traditional_score, 2)
    
    return {
        "traditional_system_score": round(traditional_score, 2),
        "mitopulse_protocol_score": mp_score,
        "lead_advantage": advantage,
        "superiority_flag": "TRUE" if advantage > 0 else "FALSE"
    }
