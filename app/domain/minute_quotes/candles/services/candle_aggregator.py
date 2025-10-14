from datetime import datetime
from collections import defaultdict
from app.domain.minute_quotes.candles.services.candle_storage import push_candle
from app.domain.minute_quotes.candles.services.indicator_calculator import calculate_and_save_indicators
from app.infra.kafka_producer import producer, delivery_report
import json

AGG_RULES = {"5m": 5, "15m": 15, "1h": 60, "4h": 240}
aggregate_cache = defaultdict(list)
last_bucket_time = {}


def parse_time_flexible(t_str: str):
    """'2025-10-13T13:22:00' 또는 '202510131322' 둘 다 처리"""
    try:
        if "T" in t_str:
            return datetime.fromisoformat(t_str)
        return datetime.strptime(t_str, "%Y%m%d%H%M")
    except Exception as e:
        print(f"⚠️ [TIME PARSE ERROR] {e} / t={t_str}", flush=True)
        return None


def aggregate_to_higher_timeframes(symbol: str, candle_1m: dict):
    candle_time = candle_1m["t"]
    candle_dt = parse_time_flexible(candle_time)
    if not candle_dt:
        return

    for tf, minutes in AGG_RULES.items():
        cache_key = (symbol, tf)

        bucket_minute = candle_dt.minute - (candle_dt.minute % minutes)
        bucket_time = candle_dt.replace(minute=bucket_minute, second=0)

        # 버킷 변경 감지 시 초기화
        if last_bucket_time.get(cache_key) != bucket_time:
            last_bucket_time[cache_key] = bucket_time
            aggregate_cache[cache_key].clear()

        aggregate_cache[cache_key].append(candle_1m)

        # 버킷의 마지막 분이면 flush
        minute_in_bucket = candle_dt.minute % minutes
        if minute_in_bucket == (minutes - 1):
            candles = aggregate_cache[cache_key]
            if not candles:
                continue

            agg = {
                "t": bucket_time.strftime("%Y%m%d%H%M"),
                "o": candles[0]["o"],
                "h": max(c["h"] for c in candles),
                "l": min(c["l"] for c in candles),
                "c": candles[-1]["c"],
                "v": sum(c["v"] for c in candles),
            }

            if "cumulative_volume" in candles[-1]:
                agg["cumulative_volume"] = candles[-1]["cumulative_volume"]
            if "cumulative_value" in candles[-1]:
                agg["cumulative_value"] = candles[-1]["cumulative_value"]
            if "tick_strength" in candles[0]:
                strengths = [
                    c.get("tick_strength", 0) for c in candles if "tick_strength" in c
                ]
                if strengths:
                    agg["tick_strength"] = sum(strengths) / len(strengths)

            push_candle(symbol, tf, agg)

            topic = f"candles.{symbol}.{tf}"
            producer.produce(
                topic,
                value=json.dumps(agg, ensure_ascii=False),
                callback=delivery_report,
            )
            producer.poll(0)
            print(f"[Kafka →] {topic}: {agg}", flush=True)

            # 지표 계산 (봉 완성 시)
            try:
                calculate_and_save_indicators(symbol, tf)
            except Exception as e:
                print(f"⚠️  지표 계산 에러 [{symbol}:{tf}]: {e}", flush=True)

            aggregate_cache[cache_key].clear()
