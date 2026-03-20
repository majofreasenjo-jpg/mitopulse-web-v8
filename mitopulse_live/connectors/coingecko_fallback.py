from typing import Any, Dict
import requests

from mitopulse_live.utils.config import COINGECKO_BASE_URL, REQUEST_TIMEOUT


class CoinGeckoFallbackClient:
    def __init__(self, base_url: str | None = None, timeout: float | None = None) -> None:
        self.base_url = (base_url or COINGECKO_BASE_URL).rstrip("/")
        self.timeout = timeout or REQUEST_TIMEOUT
        self.session = requests.Session()

    def get_simple_price(self, ids: str, vs_currencies: str = "usd") -> Dict[str, Any]:
        url = f"{self.base_url}/simple/price"
        response = self.session.get(
            url,
            params={"ids": ids, "vs_currencies": vs_currencies, "include_24hr_change": "true"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
