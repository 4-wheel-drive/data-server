from confluent_kafka import Consumer, KafkaException, KafkaError

conf = {
    "bootstrap.servers": "localhost:19092",   # Kafka 브로커 주소
    "group.id": "test-consumer-group",        # 컨슈머 그룹 ID (아무거나 지정 가능)
    "auto.offset.reset": "earliest"           # 처음부터 읽기
}

consumer = Consumer(conf)
consumer.subscribe(["quotes.candles.1m"])     # 구독할 토픽

print("📥 Kafka consumer started. Waiting for messages...")

try:
    while True:
        msg = consumer.poll(1.0)  # 1초 대기
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                raise KafkaException(msg.error())
        print(f"✅ Received message: {msg.value().decode('utf-8')}")
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
