import pandas as pd
from app.domain.indicators.redis_helper import get_indicator_from_redis

def compute_sma(prices, windows=[5, 20, 60, 120], prefix=""):
    s = pd.Series(prices)
    sma_data = {}
    for window in windows:
        if len(s) >= window:
            key = f"{prefix}sma_{window}" if prefix else f"sma_{window}"
            sma_data[key] = s.rolling(window).mean().iloc[-1]
    return sma_data

def compute_ema(prices, windows=[5, 20, 60, 120], prefix=""):
    s = pd.Series(prices)
    ema_data = {}
    for window in windows:
        if len(s) >= window:
            key = f"{prefix}ema_{window}" if prefix else f"ema_{window}"
            ema_data[key] = s.ewm(span=window, adjust=False).mean().iloc[-1]
    return ema_data

def compute_all_timeframe_ma(prices, symbol=None):
    results = {}
    
    all_windows = [5, 20, 60, 120]
    timeframes = ["1m_", "5m_", "15m_", "1h_", "4h_", "1d_"]
    
    for timeframe in timeframes:
        tf_key = timeframe.rstrip('_')
        
        for window in all_windows:
            sma_key = f"{timeframe}sma_{window}"
            ema_key = f"{timeframe}ema_{window}"
            
            if len(prices) >= window:
                sma_result = compute_sma(prices, [window], timeframe)
                ema_result = compute_ema(prices, [window], timeframe)
                results.update(sma_result)
                results.update(ema_result)
            elif symbol:
                sma_value = get_indicator_from_redis(symbol, tf_key, f"sma_{window}")
                ema_value = get_indicator_from_redis(symbol, tf_key, f"ema_{window}")
                if sma_value is not None:
                    results[sma_key] = sma_value
                if ema_value is not None:
                    results[ema_key] = ema_value
    
    return results
