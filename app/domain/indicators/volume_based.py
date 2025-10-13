# import pandas as pd
# import numpy as np

# def compute_accumulated_volume(volumes):
#     if not volumes or len(volumes) == 0:
#         return None
#     return sum(volumes)

# def compute_accumulated_trading_value(volumes, prices):
#     if not volumes or not prices or len(volumes) == 0 or len(prices) == 0:
#         return None
#     if len(volumes) != len(prices):
#         min_len = min(len(volumes), len(prices))
#         volumes = volumes[:min_len]
#         prices = prices[:min_len]
#     return sum(v * p for v, p in zip(volumes, prices))

# def compute_average_volume(volumes, window=20):
#     if not volumes or len(volumes) < window:
#         return None
#     s = pd.Series(volumes)
#     return s.rolling(window).mean().iloc[-1]

# def compute_volume_ratio(current_volume, average_volume):
#     if current_volume is None or average_volume is None or average_volume == 0:
#         return None
#     return (current_volume / average_volume) * 100

# def compare_volume_threshold(accumulated_volume, threshold):
#     if accumulated_volume is None or threshold is None:
#         return False
#     return accumulated_volume >= threshold

# def detect_volume_above_previous(current_volume, previous_volume):
#     if current_volume is None or previous_volume is None:
#         return False
#     return current_volume > previous_volume

# def detect_volume_below_previous(current_volume, previous_volume):
#     if current_volume is None or previous_volume is None:
#         return False
#     return current_volume < previous_volume

# def detect_volume_above_average(current_volume, average_volume, threshold_percent=100.0):
#     if current_volume is None or average_volume is None or average_volume == 0:
#         return False
#     ratio = (current_volume / average_volume) * 100
#     return ratio >= threshold_percent

# def detect_volume_below_average(current_volume, average_volume, threshold_percent=100.0):
#     if current_volume is None or average_volume is None or average_volume == 0:
#         return False
#     ratio = (current_volume / average_volume) * 100
#     return ratio <= threshold_percent

# def detect_accumulated_volume_above_threshold(accumulated_volume, threshold):
#     if accumulated_volume is None or threshold is None:
#         return False
#     return accumulated_volume >= threshold

# def detect_accumulated_volume_below_threshold(accumulated_volume, threshold):
#     if accumulated_volume is None or threshold is None:
#         return False
#     return accumulated_volume <= threshold

# def compute_volume_indicators(volumes, prices=None, previous_volume=None, prefix=""):
#     results = {}
    
#     if not volumes or len(volumes) == 0:
#         return results
    
#     accumulated_volume = compute_accumulated_volume(volumes)
#     current_volume = volumes[-1]
    
#     results[f'{prefix}accumulated_volume'] = accumulated_volume
#     results[f'{prefix}current_volume'] = current_volume
    
#     if prices:
#         accumulated_trading_value = compute_accumulated_trading_value(volumes, prices)
#         results[f'{prefix}accumulated_trading_value'] = accumulated_trading_value
    
#     if len(volumes) >= 20:
#         average_volume = compute_average_volume(volumes, 20)
#         results[f'{prefix}average_volume_20'] = average_volume
        
#         if average_volume:
#             volume_ratio = compute_volume_ratio(current_volume, average_volume)
#             results[f'{prefix}volume_ratio'] = volume_ratio
    
#     if previous_volume:
#         volume_change = current_volume - previous_volume
#         volume_change_percent = ((current_volume - previous_volume) / previous_volume) * 100 if previous_volume > 0 else None
#         results[f'{prefix}volume_change'] = volume_change
#         results[f'{prefix}volume_change_percent'] = volume_change_percent
        
#         results[f'{prefix}volume_above_previous'] = detect_volume_above_previous(current_volume, previous_volume)
#         results[f'{prefix}volume_below_previous'] = detect_volume_below_previous(current_volume, previous_volume)
    
#     if len(volumes) >= 20:
#         average_volume = compute_average_volume(volumes, 20)
#         if average_volume:
#             results[f'{prefix}volume_above_avg_100'] = detect_volume_above_average(current_volume, average_volume, 100.0)
#             results[f'{prefix}volume_above_avg_150'] = detect_volume_above_average(current_volume, average_volume, 150.0)
#             results[f'{prefix}volume_above_avg_200'] = detect_volume_above_average(current_volume, average_volume, 200.0)
#             results[f'{prefix}volume_below_avg_100'] = detect_volume_below_average(current_volume, average_volume, 100.0)
#             results[f'{prefix}volume_below_avg_50'] = detect_volume_below_average(current_volume, average_volume, 50.0)
    
#     if accumulated_volume:
#         results[f'{prefix}accum_vol_above_1m'] = detect_accumulated_volume_above_threshold(accumulated_volume, 1000000)
#         results[f'{prefix}accum_vol_above_5m'] = detect_accumulated_volume_above_threshold(accumulated_volume, 5000000)
#         results[f'{prefix}accum_vol_above_10m'] = detect_accumulated_volume_above_threshold(accumulated_volume, 10000000)
    
#     return results

# def compute_daily_cumulative_indicators(daily_volumes, daily_prices=None, previous_day_volume=None, previous_day_amount=None):
#     results = {}
    
#     if not daily_volumes or len(daily_volumes) == 0:
#         return results
     
#     current_day_volume = sum(daily_volumes)
#     results['cumulative_volume'] = current_day_volume
    
#     if daily_prices:
#         current_day_amount = compute_accumulated_trading_value(daily_volumes, daily_prices)
#         results['cumulative_amount'] = current_day_amount
        
#         if previous_day_amount:
#             results['cumulative_amount_vs_previous'] = current_day_amount > previous_day_amount
#             amount_ratio = (current_day_amount / previous_day_amount) * 100 if previous_day_amount > 0 else None
#             if amount_ratio:
#                 results['cumulative_amount_ratio'] = amount_ratio
    
#     if previous_day_volume:
#         results['cumulative_volume_vs_previous'] = current_day_volume > previous_day_volume
#         volume_ratio = (current_day_volume / previous_day_volume) * 100 if previous_day_volume > 0 else None
#         if volume_ratio:
#             results['cumulative_volume_ratio'] = volume_ratio
    
#     return results

# def compute_all_timeframe_volume_indicators(volumes, prices=None, previous_volume=None):
#     results = {}
    
#     timeframes = ["1m_", "5m_", "15m_", "1h_", "4h_", "1d_"]
    
#     for timeframe in timeframes:
#         timeframe_results = compute_volume_indicators(volumes, prices, previous_volume, timeframe)
#         results.update(timeframe_results)
    
#     return results
