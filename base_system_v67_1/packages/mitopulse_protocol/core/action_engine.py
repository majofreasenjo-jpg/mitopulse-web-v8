from mitopulse_protocol.models.objects import ActionObject
class ActionEngine:
    def create_action(self, action_id: str, target_id: str, action_type: str, explanation: str, policy_id: str = None):
        return ActionObject(action_id, target_id, action_type, False, explanation, policy_id)
    def approve(self, action):
        action.approved = True
        return action
