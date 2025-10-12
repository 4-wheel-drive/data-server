import json
import numpy as np
from config.redis_client import r


def get_closes(ticker: str, timeframe: str, limit=100):
    key = f"C:{ticker}:{timeframe}"
    data = r.lrange(key, -limit, -1)
    return np.array([json.loads(x)["c"] for x in data])


def ema(prices, period):
    if len(prices) < period:
        return None
    alpha = 2 / (period + 1)
    ema_val = [np.mean(prices[:period])]
    for p in prices[period:]:
        ema_val.append(alpha * p + (1 - alpha) * ema_val[-1])
    return ema_val[-1]


def calc_macd(ticker: str, timeframe: str):
    closes = get_closes(ticker, timeframe, 200)
    if len(closes) < 26:
        return None

    ema12 = ema(closes, 12)
    ema26 = ema(closes, 26)
    macd_line = ema12 - ema26
    signal_line = ema([macd_line] * 9, 9)
    histogram = macd_line - signal_line

    return {"line": macd_line, "signal": signal_line, "histogram": histogram}


def calc_bb_width(ticker: str, timeframe: str, period=20, stddev=2):
    closes = get_closes(ticker, timeframe, period)
    if len(closes) < period:
        return None
    mid = np.mean(closes)
    std = np.std(closes)
    upper = mid + stddev * std
    lower = mid - stddev * std
    width = (upper - lower) / mid
    return width
