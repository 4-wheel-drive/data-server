import json
import redis
import pandas as pd
from datetime import datetime
from kafka import KafkaProducer

redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
)

INTERVALS = ["1m", "5m", "15m", "1h", "4h"]


def get_candles(symbol: str, interval: str):
    key = f"candles:{symbol}:{interval}"
    candles = redis_client.lrange(key, 0, -1)
    if not candles:
        return None
    data = [json.loads(c) for c in candles]
    return pd.DataFrame(data)


def calc_rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(span=period, adjust=False).mean()
    ema_down = down.ewm(span=period, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))


def calc_indicators(df: pd.DataFrame):
    df["ema12"] = df["c"].ewm(span=12, adjust=False).mean()
    df["ema26"] = df["c"].ewm(span=26, adjust=False).mean()
    df["macd"] = df["ema12"] - df["ema26"]
    df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["rsi"] = calc_rsi(df["c"], 14)
    df["bb_mid"] = df["c"].rolling(20).mean()
    df["bb_std"] = df["c"].rolling(20).std()
    df["bb_upper"] = df["bb_mid"] + 2 * df["bb_std"]
    df["bb_lower"] = df["bb_mid"] - 2 * df["bb_std"]
    return df


def publish_indicator(symbol: str, interval: str, df: pd.DataFrame):
    topic = f"indicators.{symbol}.{interval}"
    latest = df.iloc[-1]

    message = {
        "t": latest["t"],
        "symbol": symbol,
        "interval": interval,
        "close": float(latest["c"]),
        "ema12": float(latest["ema12"]),
        "ema26": float(latest["ema26"]),
        "macd": float(latest["macd"]),
        "signal": float(latest["signal"]),
        "rsi": float(latest["rsi"]),
        "bb_upper": float(latest["bb_upper"]),
        "bb_mid": float(latest["bb_mid"]),
        "bb_lower": float(latest["bb_lower"]),
    }

    producer.send(topic, message)
    print(f"[Kafka] {topic} → {message}")


def run_for_symbol(symbol: str):
    for interval in INTERVALS:
        df = get_candles(symbol, interval)
        if df is None or df.empty:
            print(f"[SKIP] {symbol} - no data for {interval}")
            continue

        df = calc_indicators(df)
        publish_indicator(symbol, interval, df)


if __name__ == "__main__":
    # 예시 실행
    symbols = ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN"]  # 필요한 심볼 리스트
    for symbol in symbols:
        run_for_symbol(symbol)
