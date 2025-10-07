import pandas as pd

def compute_sma(prices, windows=[5, 10, 20, 60], prefix=""):
    """단순이동평균"""
    s = pd.Series(prices)
    sma_data = {}
    for window in windows:
        if len(s) >= window:
            key = f'{prefix}sma_{window}' if prefix else f'sma_{window}'
            sma_data[key] = s.rolling(window).mean().iloc[-1]
    return sma_data

def compute_ema(prices, windows=[5, 10, 20, 60], prefix=""):
    """지수이동평균"""
    s = pd.Series(prices)
    ema_data = {}
    for window in windows:
        if len(s) >= window:
            key = f'{prefix}ema_{window}' if prefix else f'ema_{window}'
            ema_data[key] = s.ewm(span=window, adjust=False).mean().iloc[-1]
    return ema_data

def compute_all_timeframe_ma(prices):
    results = {}
    
    if len(prices) >= 5:
        results.update(compute_sma(prices, [5, 10, 20], "1m_"))
        results.update(compute_ema(prices, [5, 10, 20], "1m_"))
    
    if len(prices) >= 10:
        results.update(compute_sma(prices, [10, 20, 50], "15m_"))
        results.update(compute_ema(prices, [10, 20, 50], "15m_"))
    
    if len(prices) >= 20:
        results.update(compute_sma(prices, [20, 50, 100], "60m_"))
        results.update(compute_ema(prices, [20, 50, 100], "60m_"))
    
    if len(prices) >= 20:
        results.update(compute_sma(prices, [20, 30, 50, 60], "1d_"))
        results.update(compute_ema(prices, [20, 30, 50, 60], "1d_"))
    
    return results

