class ExplainabilitySwarm:
    """
    V88 Explainability AI Core (The Semantic Swarm)
    Ascended from V70. Generates mathematically accurate, dynamic natural language 
    executive briefs explaining WHY God Mode executed a specific intervention.
    """
    def generate_brief(self, crypto_data: list, tradfi_data: list, metrics: dict, action: str) -> str:
        # Extract the dominant Omniverse anomalies
        vix = next((t for t in tradfi_data if t["symbol"] == "^VIX"), {})
        spy = next((t for t in tradfi_data if t["symbol"] == "SPY"), {})
        btc = next((c for c in crypto_data if c["symbol"] == "BTCUSDT"), {})
        
        vix_change = float(vix.get("price_change_percent", 0.0))
        spy_change = float(spy.get("price_change_percent", 0.0))
        btc_change = float(btc.get("price_change_percent", 0.0))

        nhi = float(metrics.get('nhi', 50.0)) * 100
        avs = float(metrics.get('avs', 50.0)) * 100

        # Build dynamic linguistic context
        context_parts = []
        if vix_change > 0.5:
            context_parts.append(f"a severe Volatility surge (VIX +{round(vix_change, 2)}%) indicating TradFi institutional fear")
        elif spy_change < -0.5:
            context_parts.append(f"significant S&P 500 capital contraction ({round(spy_change, 2)}%)")
        else:
            context_parts.append("stable macroeconomic traditional variables")

        if btc_change < -1.0:
            context_parts.append(f"intersecting with cascading cryptographic liquidity (BTC {round(btc_change, 2)}%)")
        elif btc_change > 1.0:
            context_parts.append(f"fueled by an overheated cryptographic expansion (BTC +{round(btc_change, 2)}%)")
        else:
            context_parts.append("alongside baseline cryptographic homeostasis")

        context = " ".join(context_parts)
        
        severity = "Critical" if action.lower() in ["block", "review and limit", "freeze"] else "Nominal"
        
        brief = (f"V88 OMNIVERSE SCAN: The AI Swarm detected {context}. "
                 f"Coupled with a dynamic Network Health Index (NHI: {round(nhi, 1)}%) "
                 f"and an Autonomic Viability Score (AVS: {round(avs, 1)}%), the neural tensor mandated a {severity} ['{action.upper()}'] protocol "
                 f"to intercept potential structural wave collapse.")

        return brief
