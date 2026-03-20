from .base import StateMachine
class RiskStateMachine(StateMachine):
    transitions = {
        "STABLE":["DEVIATION"],
        "DEVIATION":["PRESSURE","STABLE"],
        "PRESSURE":["INSTABILITY","DEVIATION"],
        "INSTABILITY":["CRITICAL","PRESSURE"],
        "CRITICAL":["COLLAPSE","PRESSURE"],
        "COLLAPSE":[]
    }
    def __init__(self): super().__init__("STABLE")
