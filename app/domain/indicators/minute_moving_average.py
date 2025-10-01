import pandas as pd

def compute_sma(prices, window=20):
    return pd.Series(prices).rolling(window).mean()

def compute_ema(prices, window=20):
    return pd.Series(prices).ewm(span=window, adjust=False).mean()