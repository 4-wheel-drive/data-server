import pandas as pd

def compute_bollinger_bands(prices, periods=[9, 20, 50, 60, 200], num_std=2):
    if not prices:
        return {}
    
    s = pd.Series(prices)
    results = {}
    
    for period in periods:
        if len(s) < period:
            continue
        
        ma = s.rolling(period).mean()
        std = s.rolling(period).std()
        upper = ma + num_std * std
        lower = ma - num_std * std
        bandwidth = (upper - lower) / ma * 100
        
        if not ma.empty and not pd.isna(ma.iloc[-1]):
            results[f"bb_{period}_middle"] = float(ma.iloc[-1])
        if not upper.empty and not pd.isna(upper.iloc[-1]):
            results[f"bb_{period}_upper"] = float(upper.iloc[-1])
        if not lower.empty and not pd.isna(lower.iloc[-1]):
            results[f"bb_{period}_lower"] = float(lower.iloc[-1])
        if not bandwidth.empty and not pd.isna(bandwidth.iloc[-1]):
            results[f"bb_{period}_width"] = float(bandwidth.iloc[-1])
    
    return results
