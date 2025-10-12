from collections import defaultdict
from app.domain.minute_quotes.candles.services.candle_storage import push_candle
from app.infra.kafka_producer import producer, delivery_report
import json

# 상위 타임프레임 규칙
AGG_RULES = {"5m": 5, "15m": 15, "1h": 60, "4h": 240}
aggregate_cache = defaultdict(list)


def aggregate_to_higher_timeframes(symbol: str, candle_1m: dict):
    """1m 봉 → 상위 타임프레임 집계"""
    for tf, minutes in AGG_RULES.items():
        cache_key = (symbol, tf)
        aggregate_cache[cache_key].append(candle_1m)

        if len(aggregate_cache[cache_key]) == minutes:
            candles = aggregate_cache[cache_key]

            agg = {
                "t": candles[-1]["t"],
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

            # Redis 저장
            push_candle(symbol, tf, agg)

            # Kafka 발행
            topic = f"candles.{symbol}.{tf}"
            producer.produce(
                topic,
                value=json.dumps(agg, ensure_ascii=False),
                callback=delivery_report,
            )
            producer.poll(0)
            print(f"[Kafka →] {topic}: {agg}")

            aggregate_cache[cache_key].clear()
