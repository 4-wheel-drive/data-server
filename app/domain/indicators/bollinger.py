import pandas as pd


def compute_bollinger_bands(prices, window=20, num_std=2, prefix=""):
    """
    볼린저 밴드 계산 (window=20 고정)
    prices: 종가 리스트
    prefix: 타임프레임 prefix (예: '1m_')
    """
    s = pd.Series(prices)
    ma = s.rolling(window).mean()
    std = s.rolling(window).std()
    upper = ma + num_std * std
    lower = ma - num_std * std

    base_key = f"{prefix}bb_{window}" if prefix else f"bb_{window}"
    return {
        f"{base_key}_middle": ma.iloc[-1] if not ma.empty else None,
        f"{base_key}_upper": upper.iloc[-1] if not upper.empty else None,
        f"{base_key}_lower": lower.iloc[-1] if not lower.empty else None,
    }


def compute_all_timeframe_bollinger(prices):
    """
    타임프레임별 볼린저 밴드 계산
    - TIMEFRAMES: [1m, 5m, 15m, 1h, 4h, 1d]
    - WINDOW: 20 (고정)
    """
    results = {}
    timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"]

    if len(prices) < 20:
        # 데이터가 부족하면 계산하지 않음
        return results

    for tf in timeframes:
        results.update(compute_bollinger_bands(prices, 20, 2, f"{tf}_"))

    return results


def compute_mono_timeframe_bollinger(prices, period=20, stddev=2):
    if len(prices) < period:
        return {}

    s = pd.Series(prices)
    mid = s.rolling(period).mean().iloc[-1]
    std = s.rolling(period).std().iloc[-1]

    return {
        "bollinger.upper": float(mid + stddev * std),
        "bollinger.middle": float(mid),
        "bollinger.lower": float(mid - stddev * std),
    }
