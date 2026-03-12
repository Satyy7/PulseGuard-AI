import os
import json
from dotenv import load_dotenv
from groq import Groq

from .investigation_tools import (
    get_service_metrics,
    get_recent_logs,
    get_error_rate,
    get_latency_stats,
    trace_request_flow,
    get_service_incidents,
    get_incident_details,
    get_latest_incident
)

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ------------------------------------------------
# SERVICES
# ------------------------------------------------

VALID_SERVICES = [
    
    "payment-service",
    "auth-service",
    "order-service",
    "inventory-service",
    "search-service",
    "notification-service"
]


SERVICE_MAPPING = {
    
    "payment": "payment-service",
    "auth": "auth-service",
    "order": "order-service",
    "inventory": "inventory-service",
    "search": "search-service",
    "notification": "notification-service"
}


# ------------------------------------------------
# SERVICE DETECTION
# ------------------------------------------------

def detect_service(question: str):

    q = question.lower()

    for service in VALID_SERVICES:
        if service in q:
            return service

    for key, value in SERVICE_MAPPING.items():
        if key in q:
            return value

    return None


# ------------------------------------------------
# INCIDENT TIMELINE
# ------------------------------------------------

def build_incident_timeline(events):

    timeline = []

    if not isinstance(events, list):
        return timeline

    for event in events[-5:]:

        timeline.append({
            "timestamp": event.get("timestamp"),
            "metric": event.get("metric"),
            "value": event.get("value"),
            "z_scores": event.get("z_scores")
        })

    return timeline


# ------------------------------------------------
# DATA COLLECTION
# ------------------------------------------------

def collect_investigation_data(service: str):

    incidents = get_service_incidents(service)

    if isinstance(incidents, dict) and "error" in incidents:
        return incidents

    if not incidents:
        return {"error": "No incidents found for this service"}

    latest_incident = incidents[0]
    incident_id = latest_incident["id"]

    details = get_incident_details(incident_id)

    if isinstance(details, dict) and "error" in details:
        return details

    events = details.get("events", [])

    timeline = build_incident_timeline(events)

    metrics = get_service_metrics(service)
    logs = get_recent_logs(service)
    errors = get_error_rate(service)
    latency = get_latency_stats(service)
    dependencies = trace_request_flow(service)

    return {
        "service": service,
        "timeline": timeline,
        "metrics": metrics,
        "logs": logs,
        "errors": errors,
        "latency": latency,
        "dependencies": dependencies
    }


# ------------------------------------------------
# AI RCA GENERATION
# ------------------------------------------------

def generate_ai_report(question, data):

    try:

        messages = [

            {
                "role": "system",
                "content": """
You are PulseGuard AI, an infrastructure reliability investigation assistant.

Analyze the system data and return a clear Root Cause Analysis report.

Return the report strictly using this markdown format:

## Service
(service name)

## Incident Timeline
(bullet points)

## Root Cause
(explanation)

## Impact
(explanation)

## Recommended Fix
(bullet list)
"""
            },

            {
                "role": "user",
                "content": f"""
User Question:
{question}

System Investigation Data:
{json.dumps(data, indent=2)}
"""
            }
        ]

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )

        return response.choices[0].message.content

    except Exception as e:

        return f"AI generation error: {str(e)}"


# ------------------------------------------------
# MAIN INVESTIGATION ENTRY
# ------------------------------------------------

def investigate(question: str):

    try:

        service = detect_service(question)

        if not service:

            latest = get_latest_incident()

            if isinstance(latest, dict) and "error" in latest:
                return latest

            if not latest:
                return {"error": "No recent incidents"}

            service = latest[0]["service"]

        data = collect_investigation_data(service)

        if isinstance(data, dict) and "error" in data:
            return data

        report = generate_ai_report(question, data)

        return {
            "service": service,
            "analysis": report
        }

    except Exception as e:

        return {
            "error": f"Investigation failed: {str(e)}"
        }


# ------------------------------------------------
# CLI TEST
# ------------------------------------------------

if __name__ == "__main__":

    while True:

        q = input("\nAsk PulseGuard > ")

        if q.lower() == "exit":
            break

        result = investigate(q)

        print("\nResult:\n")
        print(json.dumps(result, indent=2))