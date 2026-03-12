import requests

API_URL = "http://127.0.0.1:8000"


def safe_get(endpoint: str):
    """
    Safe wrapper for API calls
    """

    try:

        r = requests.get(f"{API_URL}{endpoint}", timeout=5)

        if r.status_code != 200:
            return {"error": f"API error {r.status_code}: {r.text}"}

        return r.json()

    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}


# ------------------------------------------------
# METRICS
# ------------------------------------------------

def get_service_metrics(service: str):
    """
    Fetch recent CPU / memory / latency / error metrics
    """
    return safe_get(f"/metrics/{service}")


def get_error_rate(service: str):
    """
    Fetch error rate metrics
    """
    return safe_get(f"/metrics/{service}/errors")


def get_latency_stats(service: str):
    """
    Fetch latency stats
    """
    return safe_get(f"/metrics/{service}/latency")


# ------------------------------------------------
# LOGS
# ------------------------------------------------

def get_recent_logs(service: str):
    """
    Fetch latest logs
    """

    logs = safe_get(f"/logs/{service}")

    if isinstance(logs, list):
        return logs[-5:]

    return logs


# ------------------------------------------------
# TRACE
# ------------------------------------------------

def trace_request_flow(service: str):
    """
    Fetch service dependency trace
    """
    return safe_get(f"/trace/{service}")


# ------------------------------------------------
# INCIDENTS
# ------------------------------------------------

def get_service_incidents(service: str):
    """
    Fetch incidents related to service
    """
    return safe_get(f"/services/{service}/incidents")


def get_incident_details(incident_id: int):
    """
    Fetch incident details
    """
    return safe_get(f"/incidents/{incident_id}")

def get_latest_incident():
    return safe_get("/incidents/live")