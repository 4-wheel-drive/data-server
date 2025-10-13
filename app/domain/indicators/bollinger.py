import pandas as pd
from app.domain.indicators.redis_helper import get_indicator_from_redis

def compute_bollinger_bands(prices, window=20, num_std=2, prefix=""):
    s = pd.Series(prices)
    ma = s.rolling(window).mean()
    std = s.rolling(window).std()
    upper = ma + num_std * std
    lower = ma - num_std * std
    
    bandwidth = (upper - lower) / ma * 100

    base_key = f"{prefix}bb_{window}" if prefix else f"bb_{window}"
    return {
        f"{base_key}_middle": ma.iloc[-1] if not ma.empty else None,
        f"{base_key}_upper": upper.iloc[-1] if not upper.empty else None,
        f"{base_key}_lower": lower.iloc[-1] if not lower.empty else None,
        f"{base_key}_width": bandwidth.iloc[-1] if not bandwidth.empty else None,
    }

def compute_all_timeframe_bollinger(prices, symbol=None):
    results = {}
    
    timeframes = ["1m_", "5m_", "15m_", "1h_", "4h_", "1d_"]
    window = 20
    stddev = 2
    
    for timeframe in timeframes:
        tf_key = timeframe.rstrip('_')
        
        if len(prices) >= window:
            results.update(compute_bollinger_bands(prices, window, stddev, timeframe))
        elif symbol:
            bb_middle = get_indicator_from_redis(symbol, tf_key, f"bb_{window}_middle")
            bb_upper = get_indicator_from_redis(symbol, tf_key, f"bb_{window}_upper")
            bb_lower = get_indicator_from_redis(symbol, tf_key, f"bb_{window}_lower")
            bb_width = get_indicator_from_redis(symbol, tf_key, f"bb_{window}_width")
            
            if bb_middle is not None:
                results[f"{timeframe}bb_{window}_middle"] = bb_middle
            if bb_upper is not None:
                results[f"{timeframe}bb_{window}_upper"] = bb_upper
            if bb_lower is not None:
                results[f"{timeframe}bb_{window}_lower"] = bb_lower
            if bb_width is not None:
                results[f"{timeframe}bb_{window}_width"] = bb_width
    
    return results


def compute_mono_timeframe_bollinger(prices, period=20, stddev=2):
    if len(prices) < period:
        return {}

    s = pd.Series(prices)
    mid = s.rolling(period).mean().iloc[-1]
    std = s.rolling(period).std().iloc[-1]

    return {
        "bollinger.upper": float(mid + stddev * std),
        "bollinger.middle": float(mid),
        "bollinger.lower": float(mid - stddev * std),
    }
