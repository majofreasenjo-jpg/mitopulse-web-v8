
import random, time
def get_live():
    return {
        "yahoo":{"AAPL":190+random.random()*5},
        "binance":{"BTC":60000+random.random()*2000},
        "timestamp":time.time()
    }
