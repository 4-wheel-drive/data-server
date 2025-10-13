# import pandas as pd
# import numpy as np

# def compute_execution_strength(buy_volume, sell_volume):
#     if buy_volume is None or sell_volume is None:
#         return None
    
#     total_volume = buy_volume + sell_volume
#     if total_volume == 0:
#         return 50.0
    
#     return (buy_volume / total_volume) * 100

# def compute_execution_strength_from_price(open_price, close_price, high_price, low_price, volume):
#     if None in [open_price, close_price, high_price, low_price, volume]:
#         return None
    
#     price_range = high_price - low_price
#     if price_range == 0:
#         return 50.0
    
#     if close_price >= open_price:
#         buy_pressure = (close_price - low_price) / price_range
#     else:
#         buy_pressure = (close_price - low_price) / price_range * 0.5
    
#     return buy_pressure * 100

# def detect_strong_buying(execution_strength, threshold=60.0):
#     if execution_strength is None:
#         return False
#     return execution_strength >= threshold

# def detect_strong_selling(execution_strength, threshold=40.0):
#     if execution_strength is None:
#         return False
#     return execution_strength <= threshold

# def compute_execution_indicators(opens, highs, lows, closes, volumes, buy_volume=None, sell_volume=None, prefix=""):
#     results = {}
    
#     if not closes or len(closes) == 0:
#         return results
    
#     if buy_volume is not None and sell_volume is not None:
#         execution_strength = compute_execution_strength(buy_volume, sell_volume)
#     elif opens and highs and lows and volumes:
#         open_price = opens[-1] if opens else None
#         high_price = highs[-1] if highs else None
#         low_price = lows[-1] if lows else None
#         close_price = closes[-1]
#         volume = volumes[-1] if volumes else None
        
#         execution_strength = compute_execution_strength_from_price(
#             open_price, close_price, high_price, low_price, volume
#         )
#     else:
#         execution_strength = None
    
#     if execution_strength is not None:
#         results[f'{prefix}execution_strength'] = execution_strength
#         results[f'{prefix}strong_buying'] = detect_strong_buying(execution_strength, 60.0)
#         results[f'{prefix}strong_selling'] = detect_strong_selling(execution_strength, 40.0)
#         results[f'{prefix}neutral_execution'] = 40.0 <= execution_strength < 60.0
    
#     return results

# def compute_all_timeframe_execution_indicators(opens, highs, lows, closes, volumes, buy_volume=None, sell_volume=None):
#     results = {}
    
#     timeframes = ["1m_", "5m_", "15m_", "1h_", "4h_", "1d_"]
    
#     for timeframe in timeframes:
#         timeframe_results = compute_execution_indicators(
#             opens, highs, lows, closes, volumes, 
#             buy_volume, sell_volume, timeframe
#         )
#         results.update(timeframe_results)
    
#     return results
