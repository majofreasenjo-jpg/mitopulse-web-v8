def build_playback_frames(graph_payload: dict, steps: list):
    base_nodes = graph_payload.get("nodes", [])
    base_links = graph_payload.get("links", [])
    wave_centers = graph_payload.get("wave_centers", [])

    frames = []
    total = max(1, len(steps))
    for idx, step in enumerate(steps, start=1):
        progress = idx / total
        node_count = max(1, min(len(base_nodes), int(len(base_nodes) * progress)))
        link_count = max(0, min(len(base_links), int(len(base_links) * progress)))
        wave_count = max(0, min(len(wave_centers), int(max(1, len(wave_centers)) * progress)))

        frames.append({
            "step": step.get("step", idx),
            "phase": step.get("phase", "emergence"),
            "metrics": {
                "nhi": step.get("nhi_snapshot"),
                "tpi": step.get("tpi_snapshot"),
                "scr": step.get("scr_snapshot"),
                "mdi": step.get("mdi_snapshot")
            },
            "nodes": base_nodes[:node_count],
            "links": base_links[:link_count],
            "wave_centers": wave_centers[:wave_count],
            "action_triggered": step.get("action_triggered", False),
            "recommended_action": step.get("recommended_action", "monitor"),
            "timestamp": step.get("timestamp", "")
        })
    return frames
