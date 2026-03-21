from mitopulse_live.normalization.market_normalizer import normalize_market_snapshot


def test_normalize_market_snapshot_shape() -> None:
    ticker = {
        "source": "binance",
        "symbol": "BTCUSDT",
        "last_price": 65000.0,
        "price_change_percent": -3.2,
        "volume_quote": 1000000.0,
    }
    klines = [
        {"close": 66000.0, "volume": 100.0},
        {"close": 65500.0, "volume": 110.0},
        {"close": 65000.0, "volume": 140.0},
    ]
    out = normalize_market_snapshot(ticker, klines)
    assert out["entity_id"] == "BTCUSDT"
    assert "protocol_payload" in out
    assert "coordination_signal" in out["protocol_payload"]
