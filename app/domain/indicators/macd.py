import pandas as pd

def compute_macd(prices, short=12, long=26, signal=9, prefix=""):
    s = pd.Series(prices)
    ema_short = s.ewm(span=short, adjust=False).mean()
    ema_long = s.ewm(span=long, adjust=False).mean()
    macd = ema_short - ema_long
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal
    
    base_key = f'{prefix}macd' if prefix else 'macd'
    return {
        f'{base_key}_line': macd.iloc[-1] if not macd.empty else None,
        f'{base_key}_signal': macd_signal.iloc[-1] if not macd_signal.empty else None,
        f'{base_key}_histogram': macd_hist.iloc[-1] if not macd_hist.empty else None
    }

def compute_all_timeframe_macd(prices):
    results = {}
    
    if len(prices) >= 26:
        results.update(compute_macd(prices, 8, 17, 5, "1m_"))
    
    if len(prices) >= 26:
        results.update(compute_macd(prices, 12, 26, 9, "15m_"))
    
    if len(prices) >= 30:
        results.update(compute_macd(prices, 15, 30, 12, "60m_"))
    
    if len(prices) >= 26:
        results.update(compute_macd(prices, 12, 26, 9, "1d_"))
    
    return results
