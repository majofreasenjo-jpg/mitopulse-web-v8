from typing import Any, Dict, List
import requests

from mitopulse_live.utils.config import BINANCE_BASE_URL, REQUEST_TIMEOUT


class BinanceSpotClient:
    def __init__(self, base_url: str | None = None, timeout: float | None = None) -> None:
        self.base_url = (base_url or BINANCE_BASE_URL).rstrip("/")
        self.timeout = timeout or REQUEST_TIMEOUT
        self.session = requests.Session()

    def _get(self, path: str, params: Dict[str, Any]) -> Any:
        url = f"{self.base_url}{path}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_24h_ticker(self, symbol: str) -> Dict[str, Any]:
        data = self._get("/api/v3/ticker/24hr", {"symbol": symbol.upper()})
        return {
            "source": "binance",
            "symbol": symbol.upper(),
            "last_price": float(data["lastPrice"]),
            "price_change_percent": float(data["priceChangePercent"]),
            "volume_base": float(data["volume"]),
            "volume_quote": float(data["quoteVolume"]),
            "high_price": float(data["highPrice"]),
            "low_price": float(data["lowPrice"]),
            "open_price": float(data["openPrice"]),
            "count": int(data["count"]),
            "raw": data,
        }

    def get_recent_klines(self, symbol: str, interval: str = "1m", limit: int = 60) -> List[Dict[str, Any]]:
        rows = self._get(
            "/api/v3/klines",
            {"symbol": symbol.upper(), "interval": interval, "limit": int(limit)},
        )
        out: List[Dict[str, Any]] = []
        for row in rows:
            out.append(
                {
                    "open_time": int(row[0]),
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                    "volume": float(row[5]),
                    "close_time": int(row[6]),
                    "quote_asset_volume": float(row[7]),
                    "number_of_trades": int(row[8]),
                }
            )
        return out
