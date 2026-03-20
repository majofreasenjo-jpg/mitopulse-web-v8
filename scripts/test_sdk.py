
from mitopulse_sdk.python_sdk.client import MitoPulseClient

client = MitoPulseClient("http://localhost:8000")
print(client.evaluate("BTCUSDT", 0.9))
