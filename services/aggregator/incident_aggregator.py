import json
import psycopg2
from collections import defaultdict, deque
from datetime import datetime

from kafka import KafkaConsumer

ANOMALY_THRESHOLD = 2
TIME_WINDOW = 40

service_anomalies = defaultdict(lambda: deque())

consumer = KafkaConsumer(
    "anomaly-events",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="latest",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

conn = psycopg2.connect(
    host="localhost",
    database="pulseguard",
    user="pulse",
    password="pulse",
    port=5432
)

cursor = conn.cursor()

print("Incident Aggregator Started")


def analyze_metric(anomaly):

    cpu = anomaly["cpu"]
    memory = anomaly["memory"]
    latency = anomaly["latency"]
    error_rate = anomaly["error_rate"]

    if latency > 500:
        return "latency", latency, "HIGH", f"Latency spike detected ({latency}ms)"

    if cpu > 90:
        return "cpu", cpu, "HIGH", f"CPU spike detected ({cpu}%)"

    if error_rate > 5:
        return "error_rate", error_rate, "HIGH", f"Error rate spike detected ({error_rate})"

    if memory > 90:
        return "memory", memory, "MEDIUM", f"Memory usage high ({memory}%)"

    return "unknown", 0, "LOW", "Minor anomaly detected"


for msg in consumer:

    anomaly = msg.value
    # print("Received anomaly:", anomaly)
    service = anomaly["service"]
    now = datetime.utcnow()

    anomalies = service_anomalies[service]
    anomalies.append(now)

    while anomalies and (now - anomalies[0]).seconds > TIME_WINDOW:
        anomalies.popleft()

    if len(anomalies) >= ANOMALY_THRESHOLD:

        trigger_metric, trigger_value, severity, reason = analyze_metric(anomaly)

        print(f"INCIDENT DETECTED → {service} | {trigger_metric} | {severity}")

        cursor.execute(
            """
            INSERT INTO incidents(service,severity,trigger_metric,trigger_value,
            cpu,memory,latency,error_rate,reason,created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                service,
                severity,
                trigger_metric,
                trigger_value,
                anomaly["cpu"],
                anomaly["memory"],
                anomaly["latency"],
                anomaly["error_rate"],
                reason,
                now
            )
        )

        conn.commit()

        anomalies.clear()