import json
import os
import time
import uuid
from typing import Any, Callable

from confluent_kafka import Consumer, KafkaError, Producer

TRANSIENT_KAFKA_ERROR_CODES = {
    code
    for code in (
        getattr(KafkaError, "UNKNOWN_TOPIC_OR_PART", None),
        getattr(KafkaError, "LEADER_NOT_AVAILABLE", None),
        getattr(KafkaError, "_ALL_BROKERS_DOWN", None),
        getattr(KafkaError, "_TRANSPORT", None),
    )
    if code is not None
}


def bootstrap_servers() -> str:
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")


def create_event(event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    event = dict(payload)
    event.setdefault("event_id", str(uuid.uuid4()))
    event["event_type"] = event_type
    event.setdefault("created_at_ms", int(time.time() * 1000))
    return event


class EventProducer:
    def __init__(self) -> None:
        self._producer = Producer({"bootstrap.servers": bootstrap_servers()})

    def publish(self, topic: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        event = create_event(event_type, payload)
        key = str(event.get("content_id", event["event_id"]))
        self._producer.produce(
            topic=topic,
            key=key.encode("utf-8"),
            value=json.dumps(event).encode("utf-8"),
        )
        self._producer.flush()
        print(f"[producer] topic={topic} content_id={event.get('content_id')}", flush=True)
        return event


def consume_forever(
    service_name: str,
    topic: str,
    handler: Callable[[dict[str, Any], EventProducer], None],
) -> None:
    consumer = Consumer(
        {
            "bootstrap.servers": bootstrap_servers(),
            "group.id": service_name,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    producer = EventProducer()
    consumer.subscribe([topic])

    print(f"[{service_name}] consuming {topic}", flush=True)

    try:
        while True:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                error = message.error()
                if error.code() in TRANSIENT_KAFKA_ERROR_CODES:
                    print(
                        f"[{service_name}] waiting for kafka topic={topic}: {error}",
                        flush=True,
                    )
                    time.sleep(2)
                    continue

                print(f"[{service_name}] kafka error: {error}", flush=True)
                continue

            event = json.loads(message.value().decode("utf-8"))

            try:
                handler(event, producer)
                consumer.commit(message)
            except Exception as exc:
                print(f"[{service_name}] handler error: {exc}", flush=True)
                # Production improvement: publish to a dead-letter topic.
    finally:
        consumer.close()
