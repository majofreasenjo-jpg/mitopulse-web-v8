def impact_calc(quorum_data: dict, benchmark_data: dict):
    # Calculate Business / Financial ROI from mitigation superiority
    is_approved = quorum_data.get("is_approved", False)
    advantage = benchmark_data.get("lead_advantage", 0)
    
    # If the network approved the mitigation, we compute the prevented capital loss
    if is_approved and advantage > 0:
        # e.g., representing $ Millions saved or risk-weighted asset protection
        roi_multiplier = 1.25
        capital_protected = advantage * roi_multiplier * 10000 
    else:
        capital_protected = 0.0
        
    return {
        "roi_generated": True if capital_protected > 0 else False,
        "capital_protected_usd": round(capital_protected, 2),
        "impact_factor": "HIGH" if capital_protected > 50000 else "LOW_MODERATE"
    }
