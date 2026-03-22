import os

APP_NAME = os.getenv("APP_NAME", "MitoPulse v79 Definitiva")
APP_VERSION = os.getenv("APP_VERSION", "79.0-definitiva")
POLL_INTERVAL_MS = int(os.getenv("POLL_INTERVAL_MS", "2200"))
