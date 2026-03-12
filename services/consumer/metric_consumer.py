import json
from kafka import KafkaConsumer, KafkaProducer

from ai_engine.anomaly_model import detect_anomaly, load_or_initialize_model

consumer = KafkaConsumer(
    "system-metrics",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="latest",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


print("PulseGuard Anomaly Consumer Started")

load_or_initialize_model()

for msg in consumer:

    metric = msg.value
    print("Received:", metric)

    is_anomaly = detect_anomaly(metric)

    if is_anomaly:

        print("ANOMALY DETECTED:", metric)

        producer.send("anomaly-events", metric)