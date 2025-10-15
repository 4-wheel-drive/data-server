from datetime import datetime
from app.domain.minute_quotes.candles.utils.time_utils import parse_tick_time
from app.domain.minute_quotes.candles.services.candle_storage import push_candle
from app.domain.minute_quotes.candles.services.candle_aggregator import (
    aggregate_to_higher_timeframes,
)
from app.infra.kafka_producer import producer, delivery_report
import json

candle_buffer = {}


def on_tick(
    symbol: str,
    price: float,
    volume: int,
    tick_time: str,
    cumulative_volume: int = None,
    cumulative_value: int = None,
    tick_strength: float = None,
    change_rate: float = None,
):
    """tick 수신 → tick Kafka 발행 + 1m 봉 누적"""
    tick_dt = parse_tick_time(tick_time)
    minute = tick_dt.replace(second=0, microsecond=0)
    key = (symbol, minute)

    tick_data = {
        "symbol": symbol,
        "tick_time": tick_dt.isoformat(),
        "price": price,
        "volume": volume,
        "cumulative_volume": cumulative_volume,
        "cumulative_value": cumulative_value,
        "tick_strength": tick_strength,
        "change_rate": change_rate,
    }

    tick_topic = f"candles.{symbol}.tick"
    producer.produce(
        topic=tick_topic,
        value=json.dumps(tick_data, ensure_ascii=False),
        callback=delivery_report,
    )
    producer.poll(0)
    print(f"[Kafka →] {tick_topic}: {tick_data}")

    if key not in candle_buffer:
        candle_buffer[key] = {
            "t": minute.isoformat(),
            "o": price,
            "h": price,
            "l": price,
            "c": price,
            "v": volume,
            "tick_strength": tick_strength,
            "cumulative_volume": cumulative_volume,
            "cumulative_value": cumulative_value,
            "change_rate": change_rate,
        }
    else:
        c = candle_buffer[key]
        c["h"] = max(c["h"], price)
        c["l"] = min(c["l"], price)
        c["c"] = price
        c["v"] += volume
        c["tick_strength"] = tick_strength
        c["cumulative_volume"] = cumulative_volume
        c["cumulative_value"] = cumulative_value
        c["change_rate"] = change_rate

    # ✅ 지난 분 봉 완료 시 Redis push + Kafka 발행
    finished_keys = [
        k for k in candle_buffer.keys() if k[0] == symbol and k[1] < minute
    ]
    for k in finished_keys:
        _, candle_minute = k
        candle = candle_buffer.pop(k)
        push_candle(symbol, "1m", candle)

        candle_topic = f"candles.{symbol}.1m"
        producer.produce(
            topic=candle_topic,
            value=json.dumps(candle, ensure_ascii=False),
            callback=delivery_report,
        )
        producer.poll(0)
        print(f"[Kafka →] {candle_topic}: {candle}")

        aggregate_to_higher_timeframes(symbol, candle)
