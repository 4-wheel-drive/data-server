import pandas as pd
import numpy as np


# ===== 캔들 패턴 탐지 함수들 =====


def detect_long_bullish_candle(opens, highs, lows, closes):
    """장대양봉 감지"""
    if len(opens) < 1:
        return False

    open_price = opens[-1]
    close_price = closes[-1]
    high_price = highs[-1]
    low_price = lows[-1]

    is_bullish = close_price > open_price
    body_size = abs(close_price - open_price)
    total_range = high_price - low_price

    is_long_candle = body_size >= total_range * 0.7
    return is_bullish and is_long_candle


def detect_long_bearish_candle(opens, highs, lows, closes):
    """장대음봉 감지"""
    if len(opens) < 1:
        return False

    open_price = opens[-1]
    close_price = closes[-1]
    high_price = highs[-1]
    low_price = lows[-1]

    is_bearish = close_price < open_price
    body_size = abs(close_price - open_price)
    total_range = high_price - low_price

    is_long_candle = body_size >= total_range * 0.7
    return is_bearish and is_long_candle


def detect_bullish_engulfing(opens, highs, lows, closes):
    """상승 잠식형 패턴 감지"""
    if len(opens) < 2:
        return False

    prev_open = opens[-2]
    prev_close = closes[-2]
    curr_open = opens[-1]
    curr_close = closes[-1]

    prev_is_bearish = prev_close < prev_open
    curr_is_bullish = curr_close > curr_open

    return (
        prev_is_bearish
        and curr_is_bullish
        and curr_open < prev_close
        and curr_close > prev_open
    )


def detect_bearish_engulfing(opens, highs, lows, closes):
    """하락 잠식형 패턴 감지"""
    if len(opens) < 2:
        return False

    prev_open = opens[-2]
    prev_close = closes[-2]
    curr_open = opens[-1]
    curr_close = closes[-1]

    prev_is_bullish = prev_close > prev_open
    curr_is_bearish = curr_close < curr_open

    return (
        prev_is_bullish
        and curr_is_bearish
        and curr_open > prev_close
        and curr_close < prev_open
    )


def detect_hammer(opens, highs, lows, closes):
    """해머 패턴 감지"""
    if len(opens) < 1:
        return False

    open_price = opens[-1]
    close_price = closes[-1]
    high_price = highs[-1]
    low_price = lows[-1]

    body_size = abs(close_price - open_price)
    upper_shadow = high_price - max(open_price, close_price)
    lower_shadow = min(open_price, close_price) - low_price
    total_range = high_price - low_price

    return (
        body_size <= total_range * 0.3
        and lower_shadow >= body_size * 2
        and upper_shadow <= body_size * 0.5
    )


def detect_shooting_star(opens, highs, lows, closes):
    """슈팅스타 패턴 감지"""
    if len(opens) < 1:
        return False

    open_price = opens[-1]
    close_price = closes[-1]
    high_price = highs[-1]
    low_price = lows[-1]

    body_size = abs(close_price - open_price)
    upper_shadow = high_price - max(open_price, close_price)
    lower_shadow = min(open_price, close_price) - low_price
    total_range = high_price - low_price

    return (
        body_size <= total_range * 0.3
        and upper_shadow >= body_size * 2
        and lower_shadow <= body_size * 0.5
    )


def detect_doji(opens, highs, lows, closes):
    """도지 패턴 감지"""
    if len(opens) < 1:
        return False

    open_price = opens[-1]
    close_price = closes[-1]
    high_price = highs[-1]
    low_price = lows[-1]

    body_size = abs(close_price - open_price)
    total_range = high_price - low_price

    return body_size <= total_range * 0.05


def detect_spinning_top(opens, highs, lows, closes):
    """스피닝탑 패턴 감지"""
    if len(opens) < 1:
        return False

    open_price = opens[-1]
    close_price = closes[-1]
    high_price = highs[-1]
    low_price = lows[-1]

    body_size = abs(close_price - open_price)
    upper_shadow = high_price - max(open_price, close_price)
    lower_shadow = min(open_price, close_price) - low_price
    total_range = high_price - low_price

    is_small_body = body_size <= total_range * 0.3
    has_both_shadows = upper_shadow > 0 and lower_shadow > 0
    balanced_shadows = abs(upper_shadow - lower_shadow) <= body_size

    return is_small_body and has_both_shadows and balanced_shadows


# ===== 패턴 계산 함수 =====


def compute_candle_pattern(opens, highs, lows, closes, pattern_name, prefix=""):
    """특정 캔들 패턴 감지"""
    pattern_functions = {
        "LONG_BULLISH_CANDLE": detect_long_bullish_candle,
        "LONG_BEARISH_CANDLE": detect_long_bearish_candle,
        "BULLISH_ENGULFING": detect_bullish_engulfing,
        "BEARISH_ENGULFING": detect_bearish_engulfing,
        "HAMMER": detect_hammer,
        "SHOOTING_STAR": detect_shooting_star,
        "DOJI": detect_doji,
        "SPINNING_TOP": detect_spinning_top,
    }

    func = pattern_functions.get(pattern_name)
    key = f"{prefix}candle_{pattern_name.lower()}"

    if func is None:
        return {key: False}

    return {key: func(opens, highs, lows, closes)}


def compute_all_timeframe_candle_patterns(opens, highs, lows, closes):
    """모든 타임프레임별 캔들 패턴 계산 (1m, 5m, 15m, 1h, 4h, 1d)"""
    results = {}

    if not (opens and highs and lows and closes):
        return results

    timeframe_patterns = {
        f"{tf}_": [
            "LONG_BULLISH_CANDLE",
            "LONG_BEARISH_CANDLE",
            "BULLISH_ENGULFING",
            "BEARISH_ENGULFING",
            "HAMMER",
            "SHOOTING_STAR",
            "DOJI",
            "SPINNING_TOP",
        ]
        for tf in ["1m", "5m", "15m", "1h", "4h", "1d"]
    }

    for timeframe, patterns in timeframe_patterns.items():
        for pattern in patterns:
            pattern_result = compute_candle_pattern(
                opens, highs, lows, closes, pattern, timeframe
            )
            results.update(pattern_result)

    return results
