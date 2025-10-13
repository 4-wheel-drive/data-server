import pandas as pd
from app.domain.indicators.redis_helper import get_indicator_from_redis

def compute_rsi(prices, period=14, prefix=""):
    s = pd.Series(prices)
    delta = s.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    roll_up = up.ewm(span=period).mean()
    roll_down = down.ewm(span=period).mean()
    rs = roll_up / roll_down
    rsi = 100 - (100 / (1 + rs))

    key = f"{prefix}rsi_{period}" if prefix else f"rsi_{period}"
    return {key: rsi.iloc[-1]} if not rsi.empty else {key: None}

def compute_all_timeframe_rsi(prices, symbol=None):
    results = {}
    
    timeframes = ["1m_", "5m_", "15m_", "1h_", "4h_", "1d_"]
    periods = [7, 14, 21]

    for timeframe in timeframes:
        tf_key = timeframe.rstrip('_')
        
        for period in periods:
            rsi_key = f"{timeframe}rsi_{period}"
            
            if len(prices) >= period:
                results.update(compute_rsi(prices, period, timeframe))
            elif symbol:
                rsi_value = get_indicator_from_redis(symbol, tf_key, f"rsi_{period}")
                if rsi_value is not None:
                    results[rsi_key] = rsi_value

    return results


def compute_mono_timeframe_rsi(prices, timeframe: str):
    """RSI 7, 14, 21 계산"""
    s = pd.Series(prices)
    delta = s.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)

    results = {}
    for period in [7, 14, 21]:
        if len(prices) < period + 1:
            continue
        roll_up = up.ewm(span=period, adjust=False).mean()
        roll_down = down.ewm(span=period, adjust=False).mean()
        rs = roll_up / roll_down
        rsi = 100 - (100 / (1 + rs))
        results[f"rsi{period}"] = float(rsi.iloc[-1])
    return results
