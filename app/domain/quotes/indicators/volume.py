import pandas as pd

def compute_rvol(volumes, period=20):
    s = pd.Series(volumes)
    vol_ma = s.rolling(window=period).mean()
    return s / vol_ma
