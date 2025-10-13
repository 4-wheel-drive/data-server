# import pandas as pd
# import numpy as np


# def compute_hold_bb_upper(prices, window=20, num_std=2, bars=1, prefix=""):
#     """볼린저밴드 상단 위 유지 계산"""
#     if len(prices) < window + bars:
#         return {f"{prefix}hold_bb_upper_{bars}bar": False}

#     s = pd.Series(prices)
#     ma = s.rolling(window).mean()
#     std = s.rolling(window).std()
#     bb_upper = ma + num_std * std

#     hold_count = 0
#     for i in range(len(prices) - 1, max(0, len(prices) - bars - 1), -1):
#         if prices[i] > bb_upper.iloc[i]:
#             hold_count += 1
#         else:
#             break

#     key = f"{prefix}hold_bb_upper_{bars}bar"
#     return {key: hold_count >= bars}


# def compute_hold_vwap(prices, volumes, bars=1, prefix=""):
#     """VWAP 상방 유지 계산"""
#     if len(prices) < bars or len(volumes) < bars:
#         return {f"{prefix}hold_vwap_{bars}bar": False}

#     s_prices = pd.Series(prices)
#     s_volumes = pd.Series(volumes)
#     vwap = (s_prices * s_volumes).cumsum() / s_volumes.cumsum()

#     hold_count = 0
#     for i in range(len(prices) - 1, max(0, len(prices) - bars - 1), -1):
#         if prices[i] > vwap.iloc[i]:
#             hold_count += 1
#         else:
#             break

#     key = f"{prefix}hold_vwap_{bars}bar"
#     return {key: hold_count >= bars}


# def compute_hold_ema(prices, period=9, bars=2, prefix=""):
#     """EMA 위 유지 계산"""
#     if len(prices) < period + bars:
#         return {f"{prefix}hold_ema{period}_{bars}bar": False}

#     s = pd.Series(prices)
#     ema = s.ewm(span=period, adjust=False).mean()

#     hold_count = 0
#     for i in range(len(prices) - 1, max(0, len(prices) - bars - 1), -1):
#         if prices[i] > ema.iloc[i]:
#             hold_count += 1
#         else:
#             break

#     key = f"{prefix}hold_ema{period}_{bars}bar"
#     return {key: hold_count >= bars}


# def compute_hold_range_high(prices, highs, window=20, bars=1, prefix=""):
#     """범위 고점 돌파 후 유지 계산"""
#     if len(prices) < window + bars or len(highs) < window + bars:
#         return {f"{prefix}hold_range_high_{bars}bar": False}

#     s_highs = pd.Series(highs)
#     range_high = s_highs.rolling(window).max()

#     hold_count = 0
#     for i in range(len(prices) - 1, max(0, len(prices) - bars - 1), -1):
#         if prices[i] >= range_high.iloc[i]:
#             hold_count += 1
#         else:
#             break

#     key = f"{prefix}hold_range_high_{bars}bar"
#     return {key: hold_count >= bars}


# def compute_hold_previous_open(prices, opens, bars=1, prefix=""):
#     """전일 시가 위 유지 계산"""
#     if len(prices) < bars or len(opens) < 1:
#         return {f"{prefix}hold_prev_open_{bars}bar": False}

#     previous_open = opens[-1]

#     hold_count = 0
#     for i in range(len(prices) - 1, max(0, len(prices) - bars - 1), -1):
#         if prices[i] >= previous_open:
#             hold_count += 1
#         else:
#             break

#     key = f"{prefix}hold_prev_open_{bars}bar"
#     return {key: hold_count >= bars}


# def compute_all_timeframe_hold(prices, highs=None, lows=None, volumes=None, opens=None):
#     """모든 타임프레임별 HOLD 지표 계산"""
#     results = {}
#     if not prices or len(prices) < 2:
#         return results

#     timeframes = ["1m_", "5m_", "15m_", "1h_", "4h_", "1d_"]

#     for tf in timeframes:
#         # Bollinger upper 유지
#         if len(prices) >= 20:
#             results.update(compute_hold_bb_upper(prices, 20, 2, 1, tf))
#             results.update(compute_hold_ema(prices, 9, 2, tf))

#         # VWAP 유지
#         if volumes and len(volumes) >= 1:
#             results.update(compute_hold_vwap(prices, volumes, 1, tf))

#         # 최근 고점 유지
#         if highs and len(highs) >= 20:
#             results.update(compute_hold_range_high(prices, highs, 20, 1, tf))

#         # 전일 시가 유지
#         if opens and len(opens) >= 1:
#             results.update(compute_hold_previous_open(prices, opens, 1, tf))

#     return results
