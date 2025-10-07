import pandas as pd

def compute_rsi(prices, period=14, prefix=""):
    s = pd.Series(prices)
    delta = s.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    roll_up = up.ewm(span=period).mean()
    roll_down = down.ewm(span=period).mean()
    rs = roll_up / roll_down
    rsi = 100 - (100 / (1 + rs))
    
    key = f'{prefix}rsi_{period}' if prefix else f'rsi_{period}'
    return {key: rsi.iloc[-1]} if not rsi.empty else {key: None}

def compute_all_timeframe_rsi(prices):
    results = {}
    
    for period in [7, 14]:
        if len(prices) >= period:
            results.update(compute_rsi(prices, period, "1m_"))
    
    for period in [14, 30, 70]:
        if len(prices) >= period:
            results.update(compute_rsi(prices, period, "15m_"))
    
    for period in [14, 21]:
        if len(prices) >= period:
            results.update(compute_rsi(prices, period, "60m_"))
    
    for period in [14, 30, 70]:
        if len(prices) >= period:
            results.update(compute_rsi(prices, period, "1d_"))
    
    if len(prices) >= 21:
        results.update(compute_rsi(prices, 21, "60m_"))
    
    if len(prices) >= 14:
        results.update(compute_rsi(prices, 14, "1d_"))
    
    return results
