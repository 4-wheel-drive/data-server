import pandas as pd

def compute_macd(prices, short=12, long=26, signal=9):
    if len(prices) < long:
        return {}
    
    s = pd.Series(prices)
    ema_short = s.ewm(span=short, adjust=False).mean()
    ema_long = s.ewm(span=long, adjust=False).mean()
    macd = ema_short - ema_long
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal
    
    results = {}
    if not macd.empty and not pd.isna(macd.iloc[-1]):
        results["macd_line"] = float(macd.iloc[-1])
    if not macd_signal.empty and not pd.isna(macd_signal.iloc[-1]):
        results["macd_signal"] = float(macd_signal.iloc[-1])
    if not macd_hist.empty and not pd.isna(macd_hist.iloc[-1]):
        results["macd_histogram"] = float(macd_hist.iloc[-1])
    
    return results
