import pandas as pd

def compute_bollinger_bands(prices, window=20, num_std=2, prefix=""):
    s = pd.Series(prices)
    ma = s.rolling(window).mean()
    std = s.rolling(window).std()
    upper = ma + num_std * std
    lower = ma - num_std * std
    
    base_key = f'{prefix}bb_{window}' if prefix else f'bb_{window}'
    return {
        f'{base_key}_middle': ma.iloc[-1] if not ma.empty else None,
        f'{base_key}_upper': upper.iloc[-1] if not upper.empty else None,
        f'{base_key}_lower': lower.iloc[-1] if not lower.empty else None
    }

def compute_all_timeframe_bollinger(prices):
    results = {}
    
    if len(prices) >= 10:
        results.update(compute_bollinger_bands(prices, 10, 2, "1m_"))
    
    if len(prices) >= 20:
        results.update(compute_bollinger_bands(prices, 20, 2, "15m_"))
    
    if len(prices) >= 20:
        results.update(compute_bollinger_bands(prices, 20, 2, "60m_"))
    
    if len(prices) >= 50:
        results.update(compute_bollinger_bands(prices, 50, 2, "1d_"))
    
    return results

