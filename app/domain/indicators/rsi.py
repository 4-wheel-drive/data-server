import pandas as pd

def compute_rsi(prices, periods=[7, 14, 21]):
    if len(prices) < max(periods) + 1:
        return {}
    
    s = pd.Series(prices)
    delta = s.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    
    results = {}
    for period in periods:
        if len(prices) < period + 1:
            continue
        
        roll_up = up.ewm(span=period, adjust=False).mean()
        roll_down = down.ewm(span=period, adjust=False).mean()
        rs = roll_up / roll_down
        rsi = 100 - (100 / (1 + rs))
        
        if not rsi.empty and not pd.isna(rsi.iloc[-1]):
            results[f"rsi_{period}"] = float(rsi.iloc[-1])
    
    return results
