def summarize_payload(payload: dict) -> str:
    entity = payload.get("entity_id", "unknown")
    source = payload.get("source", "source")
    return f"Semantic ingestion normalized event from {source} for {entity}."
