from confluent_kafka import Producer
import json
import socket

# Kafka Producer 설정
producer_config = {
    "bootstrap.servers": "localhost:19092",  # docker-compose.yml과 일치
    "client.id": socket.gethostname(),
    "linger.ms": 5,  # 배치 전송 지연 (ms)
    "acks": "1",  # 리더 브로커 확인만 대기 (속도 ↑, 안정성 중간)
    "retries": 3,  # 전송 실패 시 자동 재시도
}

producer = Producer(producer_config)


def delivery_report(err, msg):
    if err is not None:
        print(f"[Kafka x] Delivery failed: {err}")
    else:
        print(f"[Kafka o] {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")
