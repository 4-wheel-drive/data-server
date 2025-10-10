import pandas as pd
from domain.indicators.moving_average import compute_all_timeframe_ma
from domain.indicators.rsi import compute_all_timeframe_rsi
from domain.indicators.bollinger import compute_all_timeframe_bollinger
from domain.indicators.macd import compute_all_timeframe_macd
from domain.indicators.hold import compute_all_timeframe_hold
from domain.indicators.candle_pattern import compute_all_timeframe_candle_patterns
from domain.indicators.profit_loss import compute_all_timeframe_profit_loss

def compute_all_indicators(prices, highs=None, lows=None, volumes=None, entry_price=None):
    results = {}
    
    results.update(compute_all_timeframe_ma(prices))
    
    results.update(compute_all_timeframe_rsi(prices))
    
    results.update(compute_all_timeframe_bollinger(prices))
    
    results.update(compute_all_timeframe_macd(prices))
    
    results.update(compute_all_timeframe_hold(prices, highs, lows, volumes))
    
    if highs and lows:
        results.update(compute_all_timeframe_candle_patterns(prices, highs, lows, prices))
    
    if entry_price is not None:
        current_price = prices[-1] if prices else None
        if current_price:
            results.update(compute_all_timeframe_profit_loss(current_price, entry_price))
    
    if highs and lows and volumes:
        if len(highs) >= 14 and len(lows) >= 14 and len(prices) >= 14:
            results.update(compute_stochastic(highs, lows, prices))
        
        if len(highs) >= 14 and len(lows) >= 14 and len(prices) >= 14:
            results.update(compute_atr(highs, lows, prices))
        
        if len(volumes) >= 20:
            results.update(compute_volume_indicators(volumes))
    
    return results

def compute_stochastic(highs, lows, closes, k_period=14, d_period=3):
    high_series = pd.Series(highs)
    low_series = pd.Series(lows)
    close_series = pd.Series(closes)
    
    lowest_low = low_series.rolling(window=k_period).min()
    highest_high = high_series.rolling(window=k_period).max()
    
    k_percent = 100 * ((close_series - lowest_low) / (highest_high - lowest_low))
    d_percent = k_percent.rolling(window=d_period).mean()
    
    return {
        'stoch_k': k_percent.iloc[-1] if not k_percent.empty else None,
        'stoch_d': d_percent.iloc[-1] if not d_percent.empty else None
    }

def compute_atr(highs, lows, closes, period=14):
    high_series = pd.Series(highs)
    low_series = pd.Series(lows)
    close_series = pd.Series(closes)
    
    tr1 = high_series - low_series
    tr2 = abs(high_series - close_series.shift(1))
    tr3 = abs(low_series - close_series.shift(1))
    
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    
    return {
        'atr': atr.iloc[-1] if not atr.empty else None
    }

def compute_volume_indicators(volumes, period=20):
    volume_series = pd.Series(volumes)
    avg_volume = volume_series.rolling(window=period).mean()
    volume_ratio = volume_series.iloc[-1] / avg_volume.iloc[-1] if avg_volume.iloc[-1] > 0 else 1
    
    return {
        'volume_ratio': volume_ratio,
        'avg_volume': avg_volume.iloc[-1] if not avg_volume.empty else None
    }
