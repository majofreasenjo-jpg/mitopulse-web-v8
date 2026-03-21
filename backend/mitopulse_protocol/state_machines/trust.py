from .base import StateMachine
class TrustStateMachine(StateMachine):
    transitions = {
        "UNKNOWN":["NEUTRAL"],
        "NEUTRAL":["TRUSTED","COMPROMISED"],
        "TRUSTED":["RELIABLE","COMPROMISED"],
        "RELIABLE":["CRITICAL_TRUST","COMPROMISED"],
        "CRITICAL_TRUST":["COMPROMISED"],
        "COMPROMISED":["NEUTRAL"]
    }
    def __init__(self): super().__init__("UNKNOWN")
