"""
exporter.py — Custom Prometheus exporter for Sentiment API
Runs on EC2, polls /api/latest-confidence every 5s,
exposes prediction_confidence_score on port 8000.
"""

import time
import requests
from prometheus_client import start_http_server, Gauge

# ── Configuration ────────────────────────────────────────────────────────────
APP_URL      = "http://localhost:32500/api/latest-confidence"
POLL_INTERVAL = 5          # seconds between polls
EXPORTER_PORT = 8000
DEFAULT_CONF  = 1.0        # value used when endpoint is unreachable
# ─────────────────────────────────────────────────────────────────────────────

confidence_gauge = Gauge(
    "prediction_confidence_score",
    "Latest prediction confidence score from the Sentiment API"
)


def fetch_confidence() -> float:
    """Poll the app's confidence endpoint and return the value."""
    try:
        resp = requests.get(APP_URL, timeout=4)
        resp.raise_for_status()
        data = resp.json()
        return float(data.get("confidence", DEFAULT_CONF))
    except Exception as exc:
        print(f"[exporter] WARNING: could not reach {APP_URL}: {exc}")
        return DEFAULT_CONF


def main():
    print(f"[exporter] Starting Prometheus exporter on port {EXPORTER_PORT}")
    start_http_server(EXPORTER_PORT)

    while True:
        value = fetch_confidence()
        confidence_gauge.set(value)
        print(f"[exporter] prediction_confidence_score = {value:.4f}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
