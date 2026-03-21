class InvalidTransition(Exception):
    pass

class StateMachine:
    transitions = {}
    def __init__(self, initial_state: str):
        self.state = initial_state

    def transition(self, new_state: str):
        allowed = self.transitions.get(self.state, [])
        if new_state not in allowed:
            raise InvalidTransition(f"Cannot transition from {self.state} to {new_state}")
        self.state = new_state
        return self.state
