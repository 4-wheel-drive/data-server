import pandas as pd

def compute_bollinger_bands(prices, window=20, num_std=2):
    """볼린저 밴드 계산"""
    s = pd.Series(prices)
    ma = s.rolling(window).mean()
    std = s.rolling(window).std()
    upper = ma + num_std * std
    lower = ma - num_std * std
    
    return {
        'middle': ma.iloc[-1] if not ma.empty else None,
        'upper': upper.iloc[-1] if not upper.empty else None,
        'lower': lower.iloc[-1] if not lower.empty else None
    }

