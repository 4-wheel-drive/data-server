from datetime import datetime
from app.domain.minute_quotes.candles.utils.time_utils import parse_tick_time
from app.domain.minute_quotes.candles.services.candle_storage import push_candle
from app.domain.minute_quotes.candles.services.candle_aggregator import (
    aggregate_to_higher_timeframes,
)
from app.domain.minute_quotes.candles.services.indicator_calculator import calculate_and_save_indicators
from app.infra.kafka_producer import producer, delivery_report
import json


# 현재 진행 중인 1분봉 상태
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
    """tick 수신 → 1m 봉 누적 및 Redis 저장"""
    tick_dt = parse_tick_time(tick_time)
    minute = tick_dt.replace(second=0, microsecond=0)
    key = (symbol, minute)

    # 새 봉 시작
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

        # 실시간 필드 업데이트 (tick 단위 최신값 유지)
        c["tick_strength"] = tick_strength
        c["cumulative_volume"] = cumulative_volume
        c["cumulative_value"] = cumulative_value
        c["change_rate"] = change_rate

    # 지난 분 봉 완료 시 Redis에 push
    finished_keys = [
        k for k in candle_buffer.keys() if k[0] == symbol and k[1] < minute
    ]
    for k in finished_keys:
        _, candle_minute = k
        candle = candle_buffer.pop(k)
        push_candle(symbol, "1m", candle)

        topic = f"candles.{symbol}.1m"
        producer.produce(
            topic,
            value=json.dumps(candle, ensure_ascii=False),
            callback=delivery_report,
        )
        producer.poll(0)
        print(f"[Kafka →] {topic}: {candle}")

        # 1분봉 지표 계산
        try:
            calculate_and_save_indicators(symbol, "1m")
        except Exception as e:
            print(f"⚠️  1분봉 지표 계산 에러 [{symbol}]: {e}")

        aggregate_to_higher_timeframes(symbol, candle)
