# import pandas as pd
# import numpy as np

# def compute_current_price(prices):
#     if not prices or len(prices) == 0:
#         return None
#     return prices[-1]

# def compute_open_price(opens):
#     if not opens or len(opens) == 0:
#         return None
#     return opens[0]

# def compute_close_price(closes):
#     if not closes or len(closes) == 0:
#         return None
#     return closes[-1]

# def compute_high_price(highs):
#     if not highs or len(highs) == 0:
#         return None
#     return max(highs)

# def compute_low_price(lows):
#     if not lows or len(lows) == 0:
#         return None
#     return min(lows)

# def compute_gap(current_open, previous_close):
#     if current_open is None or previous_close is None:
#         return None
#     return current_open - previous_close

# def compute_gap_percent(current_open, previous_close):
#     if current_open is None or previous_close is None or previous_close == 0:
#         return None
#     return ((current_open - previous_close) / previous_close) * 100

# def compute_price_indicators(opens, highs, lows, closes, previous_close=None, prefix=""):
#     results = {}
    
#     if not closes or len(closes) == 0:
#         return results
    
#     current_price = compute_current_price(closes)
#     open_price = compute_open_price(opens) if opens else None
#     close_price = compute_close_price(closes)
#     high_price = compute_high_price(highs) if highs else None
#     low_price = compute_low_price(lows) if lows else None
    
#     results[f'{prefix}current_price'] = current_price
#     results[f'{prefix}open_price'] = open_price
#     results[f'{prefix}close_price'] = close_price
#     results[f'{prefix}high_price'] = high_price
#     results[f'{prefix}low_price'] = low_price
    
#     if previous_close and open_price:
#         gap = compute_gap(open_price, previous_close)
#         gap_percent = compute_gap_percent(open_price, previous_close)
#         results[f'{prefix}gap'] = gap
#         results[f'{prefix}gap_percent'] = gap_percent
    
#     return results

# def compute_all_timeframe_price_indicators(opens, highs, lows, closes, previous_close=None):
#     results = {}
    
#     timeframes = ["1m_", "5m_", "15m_", "1h_", "4h_", "1d_"]
    
#     for timeframe in timeframes:
#         timeframe_results = compute_price_indicators(opens, highs, lows, closes, previous_close, timeframe)
#         results.update(timeframe_results)
    
#     return results
