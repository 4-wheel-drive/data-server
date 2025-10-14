import pandas as pd

def compute_vwap(prices, volumes):
    if not prices or not volumes or len(prices) == 0 or len(volumes) == 0:
        return None
    
    s_prices = pd.Series(prices)
    s_volumes = pd.Series(volumes)
    
    if s_volumes.sum() == 0:
        return None
    
    vwap = (s_prices * s_volumes).sum() / s_volumes.sum()
    
    if not pd.isna(vwap):
        return float(vwap)
    
    return None
