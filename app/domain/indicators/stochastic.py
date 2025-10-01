import pandas as pd

def compute_stochastic(highs, lows, closes, k_period=14, d_period=3, smooth_k=3):
    if len(closes) < k_period:
        return None, None
    high_k = pd.Series(highs).rolling(k_period).max()
    low_k = pd.Series(lows).rolling(k_period).min()
    k = (pd.Series(closes) - low_k) / (high_k - low_k) * 100
    k_smooth = k.rolling(smooth_k).mean()
    d = k_smooth.rolling(d_period).mean()
    return k_smooth, d
