"""
안되는 consumer
"""

from confluent_kafka import Consumer, KafkaException, KafkaError
import json

# Kafka Consumer 설정
conf = {
    "bootstrap.servers": "my-cluster-kafka-bootstrap.kafka:9092",  # compose 설정과 일치
    "group.id": "market-consumer-group",
    "auto.offset.reset": "latest",
}

topics = [
    "candles.005930.tick",
    "candles.005930.1m",
    "candles.005930.5m",
    "candles.005930.15m",
    "candles.005930.1h",
    "candles.005930.4h",
]

consumer = Consumer(conf)
consumer.subscribe(topics)
print(f"Subscribed to topics: {topics}")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            code = msg.error().code()
            if code in (KafkaError._PARTITION_EOF, KafkaError.UNKNOWN_TOPIC_OR_PART):
                # 토픽이 아직 안 만들어졌으면 기다림
                print(f"[Topic not ready yet] {msg.topic()}")
                continue
            raise KafkaException(msg.error())

        data = msg.value().decode("utf-8")
        print(f"[{msg.topic()}] {data}")

except KeyboardInterrupt:
    print("Stopping consumer...")
finally:
    consumer.close()
