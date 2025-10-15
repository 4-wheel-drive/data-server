import json
from app.infra.redis_client import redis_client

MAX_CANDLES = {
    "1m": 200,
    "5m": 200,
    "15m": 200,
    "1h": 200,
    "4h": 200,
}


def push_candle(ticker: str, timeframe: str, candle: dict):
    """Redis에 캔들 저장 — 최신 200개만 유지 (rpush/lpush 방향 자동 감지)"""
    key = f"C:{ticker}:{timeframe}"
    max_len = MAX_CANDLES.get(timeframe, 200)

    # rpush로 추가 (기본)
    redis_client.rpush(key, json.dumps(candle))

    # trim 수행
    redis_client.ltrim(key, -max_len, -1)

    # 실제 길이 확인
    current_len = redis_client.llen(key)

    # 혹시라도 LTRIM이 실패했다면 강제로 잘라냄
    if current_len > max_len:
        redis_client.ltrim(key, -max_len, -1)
        print(f"⚠️ [FIXED] {key} trimmed again (len={current_len}→{max_len})")

    # 디버깅용 로그
    if current_len % 100 == 0:  # 100번째마다 한 번씩 찍기
        print(f"[{key}] len={current_len}, limit={max_len}")
