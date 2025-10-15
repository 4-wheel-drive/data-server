from app.infra.redis_client import redis_client
import json


def get_indicator_from_redis(symbol, timeframe, indicator_name):
    try:
        key = f"market:{symbol}:{timeframe}"
        data = redis_client.get(key)

        if data:
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            candle_data = json.loads(data)
            return candle_data.get(indicator_name)
        return None
    except Exception as e:
        return None
