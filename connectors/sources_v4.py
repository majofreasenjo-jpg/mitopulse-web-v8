from datetime import datetime, timezone
import random

def _ts():
    return datetime.now(timezone.utc).isoformat()

def yahoo_finance():
    return {"source":"Yahoo Finance","timestamp":_ts(),"items":[
        {"symbol":"AAPL","price":191.4,"change_pct":1.10},
        {"symbol":"MSFT","price":431.2,"change_pct":0.61},
        {"symbol":"SPY","price":586.3,"change_pct":0.37},
    ]}

def binance():
    return {"source":"Binance","timestamp":_ts(),"items":[
        {"symbol":"BTCUSDT","price":68120,"change_pct":1.72},
        {"symbol":"ETHUSDT","price":3405,"change_pct":2.05},
        {"symbol":"SOLUSDT","price":176.3,"change_pct":3.20},
    ]}

def fred_macro():
    return {"source":"FRED","timestamp":_ts(),"items":[
        {"series":"VIX","value":17.9},
        {"series":"US10Y","value":4.24},
        {"series":"DXY","value":104.0},
    ]}

def alpha_vantage():
    return {"source":"Alpha Vantage","timestamp":_ts(),"items":[
        {"symbol":"XOM","price":118.5},
        {"symbol":"CVX","price":154.1},
    ]}

def coingecko():
    return {"source":"CoinGecko","timestamp":_ts(),"items":[
        {"symbol":"BTC","mcap_rank":1},
        {"symbol":"ETH","mcap_rank":2},
        {"symbol":"SOL","mcap_rank":5},
    ]}

def eia_energy():
    return {"source":"EIA","timestamp":_ts(),"items":[
        {"series":"WTI","value":78.6},
        {"series":"US Gasoline Demand","value":8.7},
        {"series":"Refinery Utilization","value":89.4},
    ]}

def noaa_weather():
    return {"source":"NOAA","timestamp":_ts(),"items":[
        {"indicator":"storm_risk_port","value":"moderate"},
        {"indicator":"heatwave_refinery","value":"low"},
    ]}

def marine_traffic_like():
    return {"source":"MarineTraffic-like mock","timestamp":_ts(),"items":[
        {"vessel":"CRUDE_CARRIER_01","status":"delayed"},
        {"vessel":"PRODUCT_TANKER_02","status":"at_port"},
    ]}

def unified_live_feed():
    return {
        "feeds":[
            yahoo_finance(),
            binance(),
            fred_macro(),
            alpha_vantage(),
            coingecko(),
            eia_energy(),
            noaa_weather(),
            marine_traffic_like(),
        ]
    }
