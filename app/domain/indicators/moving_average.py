import pandas as pd


def compute_sma(prices, windows=[9, 20, 50, 60, 200], prefix=""):
    """단순이동평균 (Simple Moving Average)"""
    s = pd.Series(prices)
    sma_data = {}
    for window in windows:
        if len(s) >= window:
            key = f"{prefix}sma_{window}" if prefix else f"sma_{window}"
            sma_data[key] = s.rolling(window).mean().iloc[-1]
    return sma_data


def compute_ema(prices, windows=[9, 20, 50, 60, 200], prefix=""):
    """지수이동평균 (Exponential Moving Average)"""
    s = pd.Series(prices)
    ema_data = {}
    for window in windows:
        if len(s) >= window:
            key = f"{prefix}ema_{window}" if prefix else f"ema_{window}"
            ema_data[key] = s.ewm(span=window, adjust=False).mean().iloc[-1]
    return ema_data


def compute_all_timeframe_ma(prices):
    """
    타임프레임별 이동평균 계산
    - 1m, 5m, 15m, 1h, 4h, 1d 타임프레임 기준
    """
    results = {}

    if len(prices) >= 9:
        # 1분봉
        results.update(compute_sma(prices, [9, 20, 50], "1m_"))
        results.update(compute_ema(prices, [9, 20, 50], "1m_"))

    if len(prices) >= 20:
        # 5분봉
        results.update(compute_sma(prices, [9, 20, 50, 60], "5m_"))
        results.update(compute_ema(prices, [9, 20, 50, 60], "5m_"))

    if len(prices) >= 50:
        # 15분봉
        results.update(compute_sma(prices, [20, 50, 60, 200], "15m_"))
        results.update(compute_ema(prices, [20, 50, 60, 200], "15m_"))

    if len(prices) >= 60:
        # 1시간봉
        results.update(compute_sma(prices, [20, 50, 60, 200], "1h_"))
        results.update(compute_ema(prices, [20, 50, 60, 200], "1h_"))

    if len(prices) >= 200:
        # 4시간봉
        results.update(compute_sma(prices, [20, 50, 60, 200], "4h_"))
        results.update(compute_ema(prices, [20, 50, 60, 200], "4h_"))

    # 일봉은 다른 프로세스에서 관리하므로 제외
    return results
