from confluent_kafka import Producer
import json, socket, os

# Kafka 설정
conf = {
    "bootstrap.servers": "my-cluster-kafka-bootstrap.kafka:9092",
    "client.id": socket.gethostname()
}

producer = Producer(conf)

# 전송 결과 콜백
def delivery_report(err, msg):
    if err is not None:
        print("[KAFKA ERROR]", err)
    else:
        print(f"[KAFKA OK] topic={msg.topic()} partition={msg.partition()} offset={msg.offset()}")

# 캔들 + 보조지표 전송
def send_candle(candle: dict, indicators: dict):
    payload = {
        "candle": candle,
        "indicators": indicators
    }
    try:
        producer.produce(
            topic="quotes.candles.1m",
            key=str(candle.get("time", "")),
            value=json.dumps(payload, ensure_ascii=False),
            callback=delivery_report
        )
        producer.poll(0)
    except BufferError:
        print("[KAFKA ERROR] Local producer queue is full")
        producer.flush()

# 종료 시 안전하게 flush
def flush():
    producer.flush()
