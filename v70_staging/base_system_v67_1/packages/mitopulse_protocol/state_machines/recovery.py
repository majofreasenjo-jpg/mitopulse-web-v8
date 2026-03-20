from .base import StateMachine
class RecoveryStateMachine(StateMachine):
    transitions = {
        "CRITICAL":["CONTAINMENT"],
        "CONTAINMENT":["STABILIZATION"],
        "STABILIZATION":["RECOVERY"],
        "RECOVERY":["REINTEGRATION"],
        "REINTEGRATION":["ADAPTATION"],
        "ADAPTATION":[]
    }
    def __init__(self): super().__init__("CRITICAL")
