import json

from mitopulse_propagation.connectors.binance_spot import BinanceSpotClient
from mitopulse_propagation.engine.graph_builder import build_propagation_graph
from mitopulse_propagation.engine.propagation import inject_shock
from mitopulse_propagation.utils.config import DEFAULT_SYMBOLS, LOOKBACK_LIMIT


def main() -> None:
    client = BinanceSpotClient()
    price_series = {}

    for symbol in DEFAULT_SYMBOLS[:10]:
        klines = client.get_recent_klines(symbol, "1m", LOOKBACK_LIMIT)
        price_series[symbol] = [k["close"] for k in klines]

    graph = build_propagation_graph(price_series)
    propagation = inject_shock(graph, "BTCUSDT", initial_intensity=1.0, decay=0.74, max_hops=3)

    payload = {
        "symbols": list(price_series.keys()),
        "graph_summary": {
            "node_count": len(graph["nodes"]),
            "edge_count": len(graph["edges"]),
        },
        "shock_demo": propagation,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
