import pandas as pd

def compute_macd(prices, short=12, long=26, signal=9):
    """MACD 계산"""
    s = pd.Series(prices)
    ema_short = s.ewm(span=short, adjust=False).mean()
    ema_long = s.ewm(span=long, adjust=False).mean()
    macd = ema_short - ema_long
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal
    
    return {
        'macd': macd.iloc[-1] if not macd.empty else None,
        'signal': macd_signal.iloc[-1] if not macd_signal.empty else None,
        'histogram': macd_hist.iloc[-1] if not macd_hist.empty else None
    }

