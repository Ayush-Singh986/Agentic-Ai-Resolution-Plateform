from prometheus_client import (
    Counter,
    Histogram,
    start_http_server
)

incident_counter = Counter(
    "incident_requests_total",
    "Total incidents processed"
)

latency_metric = Histogram(
    "incident_latency_seconds",
    "Incident processing latency"
)


def initialize_metrics():

    try:
        start_http_server(8001)
        print("Prometheus metrics server started on port 8001")

    except Exception as e:
        print(
            f"Metrics server already running: {e}"
        )