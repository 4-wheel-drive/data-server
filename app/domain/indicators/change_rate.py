# import pandas as pd
# import numpy as np

# def compute_daily_change_rate(current_price, previous_close):
#     if current_price is None or previous_close is None or previous_close == 0:
#         return None
#     return ((current_price - previous_close) / previous_close) * 100

# def compute_intraday_change_rate(current_price, open_price):
#     if current_price is None or open_price is None or open_price == 0:
#         return None
#     return ((current_price - open_price) / open_price) * 100

# def detect_surge(change_rate, threshold=3.0):
#     if change_rate is None:
#         return False
#     return change_rate >= threshold

# def detect_plunge(change_rate, threshold=-3.0):
#     if change_rate is None:
#         return False
#     return change_rate <= threshold

# def detect_change_within_range(change_rate, min_threshold=-1.0, max_threshold=1.0):
#     if change_rate is None:
#         return False
#     return min_threshold <= change_rate <= max_threshold

# def compute_change_rate_indicators(current_price, open_price=None, previous_close=None, prefix=""):
#     results = {}
    
#     if current_price is None:
#         return results
    
#     if previous_close:
#         daily_change_rate = compute_daily_change_rate(current_price, previous_close)
#         if daily_change_rate is not None:
#             results[f'{prefix}daily_change_rate'] = daily_change_rate
#             results[f'{prefix}surge_3pct'] = detect_surge(daily_change_rate, 3.0)
#             results[f'{prefix}surge_5pct'] = detect_surge(daily_change_rate, 5.0)
#             results[f'{prefix}plunge_3pct'] = detect_plunge(daily_change_rate, -3.0)
#             results[f'{prefix}plunge_5pct'] = detect_plunge(daily_change_rate, -5.0)
#             results[f'{prefix}stable_1pct'] = detect_change_within_range(daily_change_rate, -1.0, 1.0)
    
#     if open_price:
#         intraday_change_rate = compute_intraday_change_rate(current_price, open_price)
#         if intraday_change_rate is not None:
#             results[f'{prefix}intraday_change_rate'] = intraday_change_rate
#             results[f'{prefix}intraday_surge_3pct'] = detect_surge(intraday_change_rate, 3.0)
#             results[f'{prefix}intraday_plunge_3pct'] = detect_plunge(intraday_change_rate, -3.0)
    
#     return results

# def compute_all_timeframe_change_rate_indicators(current_price, opens=None, previous_close=None):
#     results = {}
    
#     timeframes = ["1m_", "5m_", "15m_", "1h_", "4h_", "1d_"]
    
#     for timeframe in timeframes:
#         open_price = opens[-1] if opens and len(opens) > 0 else None
#         timeframe_results = compute_change_rate_indicators(
#             current_price, open_price, previous_close, timeframe
#         )
#         results.update(timeframe_results)
    
#     return results
