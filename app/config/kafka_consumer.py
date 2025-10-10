from confluent_kafka import Consumer, KafkaException, KafkaError

conf = {
    "bootstrap.servers": "localhost:19092",
    "group.id": "multi-timeframe-consumer",
    "auto.offset.reset": "earliest",
}

topics = [
    "quotes.candles.1m",
    "quotes.candles.5m",
    "quotes.candles.15m",
    "quotes.candles.1h",
    "quotes.candles.4h",
    "quotes.candles.1d",
]

consumer = Consumer(conf)
consumer.subscribe(topics)
print(f"📥 Subscribed to topics: {topics}")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                raise KafkaException(msg.error())

        print(f"[{msg.topic()}] ✅ {msg.value().decode('utf-8')}")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
