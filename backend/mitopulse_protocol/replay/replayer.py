from mitopulse_protocol.storage.repository import list_events

class ReplayEngine:
    def replay_summary(self, limit=500):
        events = list_events(limit)
        counts = {}
        for e in events:
            counts[e["event_type"]] = counts.get(e["event_type"], 0) + 1
        return {"events_replayed": len(events), "counts": counts}

    def replay_steps(self, entity_id: str, limit=100):
        events = [e for e in list_events(limit*20) if e["entity_id"] == entity_id]
        return events[:limit]
