
from mitopulse_trust.engine.explain import build_explanation
from mitopulse_trust.engine.audit import create_audit_entry
from mitopulse_trust.engine.trust_score import compute_trust

def main():
    signal = 0.6
    propagation = ["BTC -> ETH", "ETH -> SOL"]

    explanation = build_explanation(signal, propagation)
    trust = compute_trust(explanation["confidence"], 0.9)

    audit = create_audit_entry("BTCUSDT", "monitor", explanation)

    print("EXPLANATION:", explanation)
    print("TRUST SCORE:", trust)
    print("AUDIT:", audit)

if __name__ == "__main__":
    main()
