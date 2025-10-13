import pandas as pd
from app.domain.indicators.redis_helper import get_indicator_from_redis

def compute_macd(prices, short=12, long=26, signal=9, prefix=""):
    s = pd.Series(prices)
    ema_short = s.ewm(span=short, adjust=False).mean()
    ema_long = s.ewm(span=long, adjust=False).mean()
    macd = ema_short - ema_long
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal

    base_key = f"{prefix}macd" if prefix else "macd"
    return {
        f"{base_key}_line": macd.iloc[-1] if not macd.empty else None,
        f"{base_key}_signal": macd_signal.iloc[-1] if not macd_signal.empty else None,
        f"{base_key}_histogram": macd_hist.iloc[-1] if not macd_hist.empty else None,
    }

def compute_all_timeframe_macd(prices, symbol=None):
    results = {}
    
    timeframes = ["1m_", "5m_", "15m_", "1h_", "4h_", "1d_"]
    
    for timeframe in timeframes:
        tf_key = timeframe.rstrip('_')
        
        if len(prices) >= 26:
            results.update(compute_macd(prices, 12, 26, 9, timeframe))
        elif symbol:
            macd_line = get_indicator_from_redis(symbol, tf_key, "macd_line")
            macd_signal = get_indicator_from_redis(symbol, tf_key, "macd_signal")
            macd_histogram = get_indicator_from_redis(symbol, tf_key, "macd_histogram")
            
            if macd_line is not None:
                results[f"{timeframe}macd_line"] = macd_line
            if macd_signal is not None:
                results[f"{timeframe}macd_signal"] = macd_signal
            if macd_histogram is not None:
                results[f"{timeframe}macd_histogram"] = macd_histogram
    
    return results
