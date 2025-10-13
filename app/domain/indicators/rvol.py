import pandas as pd
from app.domain.indicators.redis_helper import get_indicator_from_redis

def compute_rvol(volumes, period=20):
    if not volumes or len(volumes) < period:
        return None
    
    s = pd.Series(volumes)
    vol_ma = s.rolling(window=period).mean()
    rvol = s / vol_ma
    
    return rvol.iloc[-1] if not rvol.empty else None

def compute_all_timeframe_rvol(volumes, symbol=None):
    results = {}
    
    if not volumes:
        return results
    
    timeframes = ["1m_", "5m_", "15m_", "1h_", "4h_", "1d_"]
    period = 20
    
    for timeframe in timeframes:
        tf_key = timeframe.rstrip('_')
        
        if len(volumes) >= period:
            rvol_value = compute_rvol(volumes, period)
            if rvol_value is not None:
                results[f"{timeframe}rvol"] = rvol_value
        elif symbol:
            cached_rvol = get_indicator_from_redis(symbol, tf_key, "rvol20")
            if cached_rvol is not None:
                results[f"{timeframe}rvol"] = cached_rvol
    
    return results

def compute_mono_timeframe_rvol(volumes, period=20):
    if not volumes or len(volumes) < period:
        return {}
    
    avg_vol = sum(volumes[-period:]) / period
    if avg_vol == 0:
        return {"rvol20": 1.0}
    
    return {"rvol20": float(round(volumes[-1] / avg_vol, 3))}
