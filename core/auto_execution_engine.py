from core.sandbox_action_executor import SandboxActionExecutor

from core.execution_constraints import ExecutionConstraints

class AutoExecutionEngine:
    def __init__(self):
        self.executor = SandboxActionExecutor()

    def run(self, decision, alerts):
        action = decision.get("action")
        entities = [a.get("entity") for a in alerts if a.get("entity")]
        constraints = ExecutionConstraints()
        entities = constraints.filter_entities(entities, alerts)

        results = []
        for ent in entities[:5]:
            res = self.executor.execute(
                entity_id=ent,
                action=action,
                reason="auto_execution_from_rfdc"
            )
            results.append(res)

        return {
            "executed": True,
            "action": action,
            "entities": entities[:5],
            "results": results
        }
