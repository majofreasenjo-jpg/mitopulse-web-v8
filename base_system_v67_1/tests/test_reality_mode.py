from mitopulse_protocol.benchmark.engine import baseline_signal, ml_simple_signal, to_protocol_payload

def test_baseline_signal():
    ticker = {"price_change_percent": -3.1, "quote_volume": 1000, "volume": 100, "last_price": 1}
    out = baseline_signal(ticker)
    assert out["triggered"] is True

def test_protocol_payload_shape():
    ticker = {"price_change_percent": -1.8, "quote_volume": 1000, "volume": 100, "last_price": 1}
    klines = [{"close": 10, "volume": 100}, {"close": 9, "volume": 130}, {"close": 9.2, "volume": 140}]
    payload = to_protocol_payload(ticker, klines, "BTCUSDT")
    assert payload["entity_id"] == "BTCUSDT"
    assert "coordination_signal" in payload
