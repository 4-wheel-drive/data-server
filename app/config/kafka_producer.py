from confluent_kafka import Producer
import json, socket

conf = {
    "bootstrap.servers": "localhost:19092",
    "client.id": socket.gethostname(),
}

producer = Producer(conf)


def delivery_report(err, msg):
    if err is not None:
        print("[KAFKA ERROR]", err)
    else:
        print(f"[KAFKA OK] topic={msg.topic()} offset={msg.offset()}")


def send_candle(candle: dict, indicators: dict, timeframe="1m"):
    """캔들 + 보조지표 전송"""
    payload = {
        "symbol": candle.get("symbol", "UNKNOWN"),
        "timeframe": timeframe,
        "candle": candle,
        "indicators": indicators,
    }

    topic = f"quotes.candles.{timeframe}"
    try:
        producer.produce(
            topic=topic,
            key=str(candle.get("time", "")),
            value=json.dumps(payload, ensure_ascii=False),
            callback=delivery_report,
        )
        producer.poll(0)
    except BufferError:
        print("[KAFKA ERROR] Local producer queue is full")
        producer.flush()


def flush():
    producer.flush()
