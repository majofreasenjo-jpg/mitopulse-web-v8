from mitopulse_propagation.engine.propagation import inject_shock


def test_inject_shock_basic() -> None:
    graph = {
        "nodes": [{"id": "BTCUSDT"}, {"id": "ETHUSDT"}, {"id": "SOLUSDT"}],
        "edges": [
            {"source": "BTCUSDT", "target": "ETHUSDT", "correlation": 0.9, "lag": 1, "lag_score": 0.8},
            {"source": "ETHUSDT", "target": "SOLUSDT", "correlation": 0.7, "lag": 1, "lag_score": 0.6},
        ],
    }
    out = inject_shock(graph, "BTCUSDT", initial_intensity=1.0, decay=0.7, max_hops=3)
    assert "impact_map" in out
    assert "ETHUSDT" in out["impact_map"]
