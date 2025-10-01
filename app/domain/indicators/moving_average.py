import pandas as pd

def compute_sma(prices, windows=[5, 10, 20, 60]):
    """단순이동평균 계산"""
    s = pd.Series(prices)
    sma_data = {}
    for window in windows:
        if len(s) >= window:
            sma_data[f'sma_{window}'] = s.rolling(window).mean().iloc[-1]
    return sma_data

def compute_ema(prices, windows=[5, 10, 20, 60]):
    """지수이동평균 계산"""
    s = pd.Series(prices)
    ema_data = {}
    for window in windows:
        if len(s) >= window:
            ema_data[f'ema_{window}'] = s.ewm(span=window, adjust=False).mean().iloc[-1]
    return ema_data

