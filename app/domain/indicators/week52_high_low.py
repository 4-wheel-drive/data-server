import pandas as pd
from app.domain.indicators.redis_helper import get_indicator_from_redis

def compute_52week_high(daily_highs, period=252):
    if not daily_highs or len(daily_highs) < period:
        return None
    
    recent_highs = daily_highs[-period:]
    return max(recent_highs)

def compute_52week_low(daily_lows, period=252):
    if not daily_lows or len(daily_lows) < period:
        return None
    
    recent_lows = daily_lows[-period:]
    return min(recent_lows)

def compute_52week_range_position(current_price, week52_high, week52_low):
    if None in [current_price, week52_high, week52_low]:
        return None
    
    if week52_high == week52_low:
        return 50.0
    
    position = (current_price - week52_low) / (week52_high - week52_low) * 100
    return position

def compute_52week_high_ratio(current_price, week52_high):
    if current_price is None or week52_high is None or week52_high == 0:
        return None
    return (current_price / week52_high) * 100

def compute_52week_low_ratio(current_price, week52_low):
    if current_price is None or week52_low is None or week52_low == 0:
        return None
    return (current_price / week52_low) * 100

def detect_52week_high_breakout(current_price, week52_high):
    if current_price is None or week52_high is None:
        return False
    return current_price > week52_high

def detect_52week_low_breakdown(current_price, week52_low):
    if current_price is None or week52_low is None:
        return False
    return current_price < week52_low

def compute_52week_indicators(daily_highs, daily_lows, current_price, period=252):
    results = {}
    
    week52_high = compute_52week_high(daily_highs, period)
    week52_low = compute_52week_low(daily_lows, period)
    
    if week52_high is not None:
        results['week52_high'] = week52_high
    
    if week52_low is not None:
        results['week52_low'] = week52_low
    
    if week52_high and week52_low:
        week52_range = week52_high - week52_low
        results['week52_range'] = week52_range
    
    if current_price:
        if week52_high and week52_low:
            position = compute_52week_range_position(current_price, week52_high, week52_low)
            if position is not None:
                results['week52_position'] = position
        
        if week52_high:
            high_ratio = compute_52week_high_ratio(current_price, week52_high)
            if high_ratio is not None:
                results['week52_high_ratio'] = high_ratio
            
            results['week52_high_breakout'] = detect_52week_high_breakout(current_price, week52_high)
        
        if week52_low:
            low_ratio = compute_52week_low_ratio(current_price, week52_low)
            if low_ratio is not None:
                results['week52_low_ratio'] = low_ratio
            
            results['week52_low_breakdown'] = detect_52week_low_breakdown(current_price, week52_low)
    
    return results

def compute_all_timeframe_52week(daily_highs, daily_lows, current_prices_by_timeframe, symbol=None):
    results = {}
    
    if not daily_highs or not daily_lows:
        return results
    
    week52_high = compute_52week_high(daily_highs, 252)
    week52_low = compute_52week_low(daily_lows, 252)
    
    if week52_high is None and symbol:
        week52_high = get_indicator_from_redis(symbol, "1d", "week52_high")
    
    if week52_low is None and symbol:
        week52_low = get_indicator_from_redis(symbol, "1d", "week52_low")
    
    if week52_high:
        results['week52_high'] = week52_high
    
    if week52_low:
        results['week52_low'] = week52_low
    
    if week52_high and week52_low:
        results['week52_range'] = week52_high - week52_low
    
    timeframes = ["1m_", "5m_", "15m_", "1h_", "4h_", "1d_"]
    
    for timeframe in timeframes:
        if timeframe in current_prices_by_timeframe:
            current_price = current_prices_by_timeframe[timeframe]
            
            if week52_high and week52_low:
                position = compute_52week_range_position(current_price, week52_high, week52_low)
                if position is not None:
                    results[f"{timeframe}week52_position"] = position
            
            if week52_high:
                high_ratio = compute_52week_high_ratio(current_price, week52_high)
                if high_ratio is not None:
                    results[f"{timeframe}week52_high_ratio"] = high_ratio
                
                results[f"{timeframe}week52_high_breakout"] = detect_52week_high_breakout(current_price, week52_high)
            
            if week52_low:
                low_ratio = compute_52week_low_ratio(current_price, week52_low)
                if low_ratio is not None:
                    results[f"{timeframe}week52_low_ratio"] = low_ratio
                
                results[f"{timeframe}week52_low_breakdown"] = detect_52week_low_breakdown(current_price, week52_low)
    
    return results
