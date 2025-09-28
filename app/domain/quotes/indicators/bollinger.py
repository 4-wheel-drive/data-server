import pandas as pd

def compute_bollinger(prices, window=20, num_std=2):
    s = pd.Series(prices)
    ma = s.rolling(window).mean()
    std = s.rolling(window).std(ddof=0)
    upper = ma + num_std * std
    lower = ma - num_std * std
    return ma, upper, lower
