# import pandas as pd
# import numpy as np


# def compute_profit_loss_percent(current_price, entry_price):
#     """수익률 계산 (%)"""
#     if entry_price == 0:
#         return 0.0
#     return ((current_price - entry_price) / entry_price) * 100


# def compute_profit_loss_amount(current_price, entry_price):
#     """수익금액 계산"""
#     return current_price - entry_price


# def detect_stop_loss(current_price, entry_price, stop_loss_percent=-3.0):
#     """손절 조건 충족 여부"""
#     profit_loss_percent = compute_profit_loss_percent(current_price, entry_price)
#     return profit_loss_percent <= stop_loss_percent


# def detect_take_profit(current_price, entry_price, take_profit_percent=7.0):
#     """익절 조건 충족 여부"""
#     profit_loss_percent = compute_profit_loss_percent(current_price, entry_price)
#     return profit_loss_percent >= take_profit_percent


# def detect_profit_loss_zone(
#     current_price, entry_price, stop_loss_percent=-3.0, take_profit_percent=7.0
# ):
#     """수익/손실 구간 판별"""
#     profit_loss_percent = compute_profit_loss_percent(current_price, entry_price)
#     if profit_loss_percent <= stop_loss_percent:
#         return "STOP_LOSS"
#     elif profit_loss_percent >= take_profit_percent:
#         return "TAKE_PROFIT"
#     else:
#         return "HOLD"


# def compute_profit_loss_indicators(current_price, entry_price, prefix=""):
#     """기본 수익률/손익구간 계산"""
#     results = {}
#     if entry_price is None or entry_price == 0:
#         return results

#     profit_loss_percent = compute_profit_loss_percent(current_price, entry_price)
#     profit_loss_amount = compute_profit_loss_amount(current_price, entry_price)

#     stop_loss_3 = detect_stop_loss(current_price, entry_price, -3.0)
#     take_profit_7 = detect_take_profit(current_price, entry_price, 7.0)
#     stop_loss_5 = detect_stop_loss(current_price, entry_price, -5.0)
#     take_profit_15 = detect_take_profit(current_price, entry_price, 15.0)

#     zone_3_7 = detect_profit_loss_zone(current_price, entry_price, -3.0, 7.0)
#     zone_5_15 = detect_profit_loss_zone(current_price, entry_price, -5.0, 15.0)

#     results[f"{prefix}profit_loss_percent"] = profit_loss_percent
#     results[f"{prefix}profit_loss_amount"] = profit_loss_amount
#     results[f"{prefix}stop_loss_3pct"] = stop_loss_3
#     results[f"{prefix}stop_loss_5pct"] = stop_loss_5
#     results[f"{prefix}take_profit_7pct"] = take_profit_7
#     results[f"{prefix}take_profit_15pct"] = take_profit_15
#     results[f"{prefix}profit_zone_3_7"] = zone_3_7
#     results[f"{prefix}profit_zone_5_15"] = zone_5_15

#     return results


# def compute_all_timeframe_profit_loss(current_price, entry_price):
#     """모든 타임프레임별 수익률 계산"""
#     results = {}
#     if entry_price is None or entry_price == 0:
#         return results

#     # ✅ 통일된 타임프레임 리스트
#     timeframes = ["1m_", "5m_", "15m_", "1h_", "4h_", "1d_"]

#     for tf in timeframes:
#         results.update(compute_profit_loss_indicators(current_price, entry_price, tf))

#     return results


# def compute_profit_loss_summary(current_price, entry_price):
#     """단일 종목 수익/손실 요약"""
#     if entry_price is None or entry_price == 0:
#         return {}

#     profit_loss_percent = compute_profit_loss_percent(current_price, entry_price)
#     profit_loss_amount = compute_profit_loss_amount(current_price, entry_price)

#     if profit_loss_percent > 0:
#         status = "PROFIT"
#         status_kr = "수익"
#     elif profit_loss_percent < 0:
#         status = "LOSS"
#         status_kr = "손실"
#     else:
#         status = "BREAKEVEN"
#         status_kr = "손익분기"

#     return {
#         "profit_loss_percent": profit_loss_percent,
#         "profit_loss_amount": profit_loss_amount,
#         "profit_status": status,
#         "profit_status_kr": status_kr,
#         "current_price": current_price,
#         "entry_price": entry_price,
#     }
