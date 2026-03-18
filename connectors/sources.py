import random
from datetime import datetime, timezone

def yahoo_finance():
    now = datetime.now(timezone.utc).isoformat()
    return {
        "source": "Yahoo Finance",
        "timestamp": now,
        "items": [
            {"symbol":"AAPL","price":191.2,"change_pct":1.14},
            {"symbol":"MSFT","price":432.8,"change_pct":0.58},
            {"symbol":"NVDA","price":129.6,"change_pct":2.31},
            {"symbol":"SPY","price":586.4,"change_pct":0.41}
        ]
    }

def binance():
    now = datetime.now(timezone.utc).isoformat()
    return {
        "source": "Binance",
        "timestamp": now,
        "items": [
            {"symbol":"BTCUSDT","price":68250,"change_pct":1.85},
            {"symbol":"ETHUSDT","price":3410,"change_pct":2.14},
            {"symbol":"SOLUSDT","price":178,"change_pct":3.45}
        ]
    }

def fred_macro_mock():
    now = datetime.now(timezone.utc).isoformat()
    return {
        "source": "FRED / Macro Mock",
        "timestamp": now,
        "items": [
            {"series":"DXY","value":104.1},
            {"series":"US10Y","value":4.23},
            {"series":"VIX","value":17.8},
            {"series":"WTI","value":78.4}
        ]
    }

def unified_live_feed():
    return {
        "feeds": [yahoo_finance(), binance(), fred_macro_mock()]
    }
