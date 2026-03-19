
import random, time

def yahoo_live():
    return [{"symbol":"AAPL","price":190+random.random()*5}]

def binance_live():
    return [{"symbol":"BTC","price":60000+random.random()*2000}]

def macro_live():
    return [{"indicator":"VIX","value":15+random.random()*10}]

def unified():
    return {
        "yahoo": yahoo_live(),
        "binance": binance_live(),
        "macro": macro_live(),
        "timestamp": time.time()
    }
