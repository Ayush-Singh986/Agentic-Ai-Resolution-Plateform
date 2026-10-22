import json

KAFKA_AVAILABLE = False

try:

    from kafka import KafkaProducer

    producer = KafkaProducer(

        bootstrap_servers="localhost:9092",

        value_serializer=lambda x:
            json.dumps(x).encode("utf-8")
    )

    KAFKA_AVAILABLE = True

    print("Kafka connected")

except Exception:

    print(
        "Kafka unavailable. Events will be logged locally."
    )


def publish_event(event):

    if KAFKA_AVAILABLE:

        producer.send(
            "incident-events",
            value=event
        )

        producer.flush()

    else:

        print(
            f"EVENT => {event}"
        )