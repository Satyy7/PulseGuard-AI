from fastapi import FastAPI
from db.database import get_db
from ai_engine.investigation_agent import investigate

app = FastAPI(title="PulseGuard API")


@app.get("/")
def root():
    return {"message": "PulseGuard API running"}

@app.get("/incidents")
def get_incidents():

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, service, severity, trigger_metric,
        trigger_value, reason, created_at
        FROM incidents
        ORDER BY created_at DESC
        LIMIT 20
        """
    )

    rows = cur.fetchall()

    incidents = []

    for r in rows:

        incidents.append({
            "id": r[0],
            "service": r[1],
            "severity": r[2],
            "metric": r[3],
            "value": r[4],
            "reason": r[5],
            "time": r[6]
        })

    return incidents

@app.get("/services/{service}/incidents")
def get_service_incidents(service: str):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, severity, trigger_metric,
        trigger_value, reason, created_at
        FROM incidents
        WHERE service=%s
        ORDER BY created_at DESC
        LIMIT 10
        """,
        (service,)
    )

    rows = cur.fetchall()

    return [
        {
            "id": r[0],
            "severity": r[1],
            "metric": r[2],
            "value": r[3],
            "reason": r[4],
            "time": r[5]
        }
        for r in rows
    ]

@app.get("/dashboard/overview")
def dashboard_overview():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM incidents")
    incidents = cur.fetchone()[0]

    cur.execute("""
        SELECT service, severity, created_at
        FROM incidents
        ORDER BY created_at DESC
        LIMIT 5
    """)

    latest_incidents = cur.fetchall()

    return {
        "total_incidents": incidents,
        "latest_incidents": [
            {
                "service": r[0],
                "severity": r[1],
                "time": r[2]
            }
            for r in latest_incidents
        ]
    }

from pydantic import BaseModel


class InvestigationRequest(BaseModel):
    question: str


@app.post("/investigate")
def investigate_incident(req: InvestigationRequest):

    result = investigate(req.question)

    return result

@app.get("/incidents/live")
def live_incidents():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT service, severity,
        trigger_metric, trigger_value,
        created_at
        FROM incidents
        ORDER BY created_at DESC
        LIMIT 5
    """)

    rows = cur.fetchall()

    return [
        {
            "service": r[0],
            "severity": r[1],
            "metric": r[2],
            "value": r[3],
            "time": r[4]
        }
        for r in rows
    ]

@app.get("/metrics/{service}")
def get_service_metrics(service: str):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT cpu, memory, latency, error_rate, created_at
        FROM incidents
        WHERE service=%s
        ORDER BY created_at DESC
        LIMIT 10
    """, (service,))

    rows = cur.fetchall()

    return [
        {
            "cpu": r[0],
            "memory": r[1],
            "latency": r[2],
            "error_rate": r[3],
            "timestamp": r[4]
        }
        for r in rows
    ]

@app.get("/metrics/{service}/errors")
def get_error_rate(service: str):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT error_rate, created_at
        FROM incidents
        WHERE service=%s
        ORDER BY created_at DESC
        LIMIT 10
    """, (service,))

    rows = cur.fetchall()

    return [
        {
            "error_rate": r[0],
            "timestamp": r[1]
        }
        for r in rows
    ]

@app.get("/metrics/{service}/latency")
def get_latency(service: str):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT latency, created_at
        FROM incidents
        WHERE service=%s
        ORDER BY created_at DESC
        LIMIT 10
    """, (service,))

    rows = cur.fetchall()

    return [
        {
            "latency": r[0],
            "timestamp": r[1]
        }
        for r in rows
    ]

@app.get("/logs/{service}")
def get_logs(service: str):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT severity, reason, created_at
        FROM incidents
        WHERE service=%s
        ORDER BY created_at DESC
        LIMIT 5
    """, (service,))

    rows = cur.fetchall()

    logs = []

    for r in rows:

        logs.append({
            "timestamp": r[2],
            "level": r[0],
            "message": r[1]
        })

    return logs

SERVICE_DEPENDENCIES = {

    "gateway-service": ["auth-service", "order-service"],

    "auth-service": ["database"],

    "payment-service": ["auth-service", "database"],

    "order-service": ["inventory-service", "payment-service"],

    "inventory-service": ["database"]
}


@app.get("/trace/{service}")
def trace(service: str):

    dependencies = SERVICE_DEPENDENCIES.get(service, [])

    return {
        "service": service,
        "dependencies": dependencies
    }

@app.get("/incidents/{incident_id}")
def get_incident_details(incident_id: int):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, service, severity, trigger_metric,
        trigger_value, reason, created_at
        FROM incidents
        WHERE id=%s
    """, (incident_id,))

    row = cur.fetchone()

    if not row:
        return {"error": "Incident not found"}

    return {
        "id": row[0],
        "service": row[1],
        "severity": row[2],
        "metric": row[3],
        "value": row[4],
        "reason": row[5],
        "timestamp": row[6],
        "events": [
            {
                "timestamp": row[6],
                "metric": row[3],
                "value": row[4],
                "z_scores": None
            }
        ]
    }