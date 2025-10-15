import pandas as pd

def compute_rvol(volumes, period=20):
    if not volumes or len(volumes) < period:
        return None
    
    s = pd.Series(volumes)
    vol_ma = s.rolling(window=period).mean()
    rvol = s / vol_ma
    
    if not rvol.empty and not pd.isna(rvol.iloc[-1]):
        return float(rvol.iloc[-1])
    
    return None
