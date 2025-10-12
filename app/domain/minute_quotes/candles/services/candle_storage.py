import json
from app.infra.redis_client import redis_client

MAX_CANDLES = {
    "1m": 500,
    "5m": 300,
    "15m": 200,
    "1h": 200,
    "4h": 200,
}


def push_candle(ticker: str, timeframe: str, candle: dict):
    """새 봉 Redis에 추가 (capped list 유지)"""
    key = f"C:{ticker}:{timeframe}"
    max_len = MAX_CANDLES.get(timeframe, 200)
    redis_client.rpush(key, json.dumps(candle))
    redis_client.ltrim(key, -max_len, -1)
