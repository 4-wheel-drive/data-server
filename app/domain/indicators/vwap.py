import pandas as pd
from app.domain.indicators.redis_helper import get_indicator_from_redis

def compute_vwap(prices, volumes):
    if not prices or not volumes or len(prices) == 0 or len(volumes) == 0:
        return None
    
    s_prices = pd.Series(prices)
    s_volumes = pd.Series(volumes)
    
    if s_volumes.sum() == 0:
        return None
    
    vwap = (s_prices * s_volumes).sum() / s_volumes.sum()
    return vwap

def compute_all_timeframe_vwap(prices, volumes, symbol=None):
    results = {}
    
    if not prices or not volumes:
        return results
    
    timeframes = ["1m_", "5m_", "15m_", "1h_", "4h_", "1d_"]
    
    for timeframe in timeframes:
        tf_key = timeframe.rstrip('_')
        
        vwap_value = compute_vwap(prices, volumes)
        
        if vwap_value is not None:
            results[f"{timeframe}vwap"] = vwap_value
        elif symbol:
            cached_vwap = get_indicator_from_redis(symbol, tf_key, "vwap")
            if cached_vwap is not None:
                results[f"{timeframe}vwap"] = cached_vwap
    
    return results

def compute_mono_timeframe_vwap(closes, volumes):
    if not closes or not volumes or sum(volumes) == 0:
        return {}
    
    vwap = sum(c * v for c, v in zip(closes, volumes)) / sum(volumes)
    return {"vwap": float(vwap)}
