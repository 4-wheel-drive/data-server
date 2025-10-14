import pandas as pd

def compute_opening_range_indicators(highs, lows, closes):
    results = {}
    
    if not highs or not lows or len(highs) == 0 or len(lows) == 0:
        return results
    
    or_high = float(highs[0])
    or_low = float(lows[0])
    or_range = or_high - or_low
    
    results["or_high"] = or_high
    results["or_low"] = or_low
    results["or_range"] = or_range
    
    return results

