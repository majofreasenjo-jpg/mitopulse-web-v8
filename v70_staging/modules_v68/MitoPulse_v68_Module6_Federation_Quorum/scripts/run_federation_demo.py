from mitopulse_federation.network.registry import default_validators
from mitopulse_federation.network.broadcast import build_demo_votes
from mitopulse_federation.engine.quorum import weighted_quorum
from mitopulse_federation.engine.audit import build_federated_audit


def main():
    validators = default_validators()
    votes = build_demo_votes("BTCUSDT", 0.87, validators)
    quorum = weighted_quorum(votes, threshold=0.67)
    action = "block" if quorum["approved"] else "approve"
    audit = build_federated_audit("BTCUSDT", action, votes, quorum)

    print("VOTES:", votes)
    print("QUORUM:", quorum)
    print("AUDIT:", audit)


if __name__ == "__main__":
    main()
