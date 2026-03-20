class ExecutionConstraints:
    def __init__(self, max_block_ratio=0.3, require_min_alerts=2):
        self.max_block_ratio = max_block_ratio
        self.require_min_alerts = require_min_alerts

    def filter_entities(self, entities, alerts):
        if len(alerts) < self.require_min_alerts:
            return []

        max_allowed = max(1, int(len(entities) * self.max_block_ratio))
        return entities[:max_allowed]
