import json
import random
import time
from datetime import datetime, timezone

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable


services = [
    "auth-service",
    "payment-service",
    "order-service",
    "inventory-service",
    "notification-service",
    "search-service"
]


def create_producer():

    retries = 10

    for attempt in range(retries):

        try:

            producer = KafkaProducer(
                bootstrap_servers=["localhost:9092"],
                api_version=(2,8,0),
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                retries=5,
                acks="all",
                linger_ms=10
            )

            print("Connected to Kafka broker")
            return producer

        except NoBrokersAvailable:

            print("Kafka unavailable, retrying...")
            time.sleep(5)

    raise Exception("Could not connect to Kafka broker")


import time

start_time = time.time()

def generate_metric():

    cpu = random.randint(40, 65)
    memory = random.randint(40, 70)
    latency = random.randint(120, 250)
    error_rate = random.randint(0, 2)

    # anomaly probability
    if random.random() < 0.15:

        spike_type = random.choice(["cpu","memory","latency","error"])

        if spike_type == "cpu":
            cpu = random.randint(90, 98)

        elif spike_type == "memory":
            memory = random.randint(90, 98)

        elif spike_type == "latency":
            latency = random.randint(500, 700)

        elif spike_type == "error":
            error_rate = random.randint(6, 10)

    service = random.choice(services)

    metric = {
        "service": service,
        "cpu": cpu,
        "memory": memory,
        "latency": latency,
        "error_rate": error_rate,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return metric


def main():

    producer = create_producer()

    try:

        while True:

            metric = generate_metric()

            producer.send("system-metrics", metric)

            print("Sent:", metric)

            time.sleep(1)

    except KeyboardInterrupt:

        print("Generator stopped")

    finally:

        producer.flush()
        producer.close()


if __name__ == "__main__":
    main()