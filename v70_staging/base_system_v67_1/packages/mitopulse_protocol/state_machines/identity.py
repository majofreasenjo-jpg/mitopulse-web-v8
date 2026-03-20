from .base import StateMachine
class IdentityStateMachine(StateMachine):
    transitions = {
        "UNDEFINED":["OBSERVED"],
        "OBSERVED":["CONTEXTUALIZED"],
        "CONTEXTUALIZED":["TRUSTED"],
        "TRUSTED":["VERIFIED"],
        "VERIFIED":["ANCHORED"],
        "ANCHORED":[]
    }
    def __init__(self): super().__init__("UNDEFINED")
