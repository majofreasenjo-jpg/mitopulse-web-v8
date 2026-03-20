from typing import Dict, Iterable, List

from mitopulse_live.connectors.binance_spot import BinanceSpotClient
from mitopulse_live.normalization.market_normalizer import normalize_market_snapshot


def build_multi_asset_snapshot(symbols: Iterable[str]) -> List[Dict]:
    client = BinanceSpotClient()
    out: List[Dict] = []
    for symbol in symbols:
        ticker = client.get_24h_ticker(symbol)
        klines = client.get_recent_klines(symbol, "1m", 60)
        out.append(normalize_market_snapshot(ticker, klines))
    return out
