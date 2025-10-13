import pandas as pd
from app.domain.indicators.redis_helper import get_indicator_from_redis

def compute_opening_range_high(highs, period=5):
    if not highs or len(highs) < period:
        return None
    
    opening_highs = highs[:period]
    return max(opening_highs)

def compute_opening_range_low(lows, period=5):
    if not lows or len(lows) < period:
        return None
    
    opening_lows = lows[:period]
    return min(opening_lows)

def detect_opening_range_high_breakout(current_price, opening_range_high):
    if current_price is None or opening_range_high is None:
        return False
    return current_price > opening_range_high

def detect_opening_range_low_breakdown(current_price, opening_range_low):
    if current_price is None or opening_range_low is None:
        return False
    return current_price < opening_range_low

def compute_opening_range_indicators(highs, lows, closes, period=5, prefix=""):
    results = {}
    
    if not highs or not lows or not closes:
        return results
    
    is_locked = len(highs) > period
    
    or_high = compute_opening_range_high(highs, period)
    or_low = compute_opening_range_low(lows, period)
    current_price = closes[-1] if closes else None
    
    results[f"{prefix}or_locked_{period}"] = is_locked
    
    if or_high is not None:
        results[f"{prefix}or_high_{period}"] = or_high
    
    if or_low is not None:
        results[f"{prefix}or_low_{period}"] = or_low
    
    if or_high is not None and or_low is not None:
        or_range = or_high - or_low
        results[f"{prefix}or_range_{period}"] = or_range
    
    if is_locked and current_price and or_high:
        results[f"{prefix}or_high_breakout_{period}"] = detect_opening_range_high_breakout(current_price, or_high)
    
    if is_locked and current_price and or_low:
        results[f"{prefix}or_low_breakdown_{period}"] = detect_opening_range_low_breakdown(current_price, or_low)
    
    return results

def compute_all_timeframe_opening_range(highs, lows, closes, symbol=None):
    results = {}
    
    if not highs or not lows or not closes:
        return results
    
    timeframes = ["1m_", "5m_", "15m_", "1h_", "4h_", "1d_"]
    periods = [5, 10, 15, 30]
    
    for timeframe in timeframes:
        tf_key = timeframe.rstrip('_')
        
        for period in periods:
            if len(highs) >= period and len(lows) >= period:
                results.update(compute_opening_range_indicators(highs, lows, closes, period, timeframe))
            elif symbol:
                or_locked = get_indicator_from_redis(symbol, tf_key, f"or_locked_{period}")
                or_high = get_indicator_from_redis(symbol, tf_key, f"or_high_{period}")
                or_low = get_indicator_from_redis(symbol, tf_key, f"or_low_{period}")
                or_range = get_indicator_from_redis(symbol, tf_key, f"or_range_{period}")
                or_high_breakout = get_indicator_from_redis(symbol, tf_key, f"or_high_breakout_{period}")
                or_low_breakdown = get_indicator_from_redis(symbol, tf_key, f"or_low_breakdown_{period}")
                
                if or_locked is not None:
                    results[f"{timeframe}or_locked_{period}"] = or_locked
                if or_high is not None:
                    results[f"{timeframe}or_high_{period}"] = or_high
                if or_low is not None:
                    results[f"{timeframe}or_low_{period}"] = or_low
                if or_range is not None:
                    results[f"{timeframe}or_range_{period}"] = or_range
                if or_high_breakout is not None:
                    results[f"{timeframe}or_high_breakout_{period}"] = or_high_breakout
                if or_low_breakdown is not None:
                    results[f"{timeframe}or_low_breakdown_{period}"] = or_low_breakdown
    
    return results
