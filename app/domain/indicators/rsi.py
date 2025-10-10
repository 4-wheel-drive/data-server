import pandas as pd


def compute_rsi(prices, period=14, prefix=""):
    s = pd.Series(prices)
    delta = s.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    roll_up = up.ewm(span=period).mean()
    roll_down = down.ewm(span=period).mean()
    rs = roll_up / roll_down
    rsi = 100 - (100 / (1 + rs))

    key = f"{prefix}rsi_{period}" if prefix else f"rsi_{period}"
    return {key: rsi.iloc[-1]} if not rsi.empty else {key: None}


def compute_all_timeframe_rsi(prices):
    """
    타임프레임별 RSI 계산 (표준화 버전)
    - 타임프레임: 1m, 5m, 15m, 1h, 4h
    - 기간(period): 7, 14, 21
    """
    results = {}
    timeframes = ["1m", "5m", "15m", "1h", "4h"]

    for tf in timeframes:
        for period in [7, 14, 21]:
            if len(prices) >= period:
                results.update(compute_rsi(prices, period, f"{tf}_"))

    return results
