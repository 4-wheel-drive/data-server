import pandas as pd

def compute_sma(prices, periods=[9, 20, 50, 60, 200]):
    if not prices:
        return {}
    
    s = pd.Series(prices)
    sma_data = {}
    
    for period in periods:
        if len(s) >= period:
            sma_value = s.rolling(period).mean().iloc[-1]
            if not pd.isna(sma_value):
                sma_data[f"sma_{period}"] = float(sma_value)
    
    return sma_data

def compute_ema(prices, periods=[9, 20, 50, 60, 200]):
    if not prices:
        return {}
    
    s = pd.Series(prices)
    ema_data = {}
    
    for period in periods:
        if len(s) >= period:
            ema_value = s.ewm(span=period, adjust=False).mean().iloc[-1]
            if not pd.isna(ema_value):
                ema_data[f"ema_{period}"] = float(ema_value)
    
    return ema_data
