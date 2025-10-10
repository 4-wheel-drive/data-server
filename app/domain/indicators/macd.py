import pandas as pd


def compute_macd(prices, short=12, long=26, signal=9, prefix=""):
    """MACD 계산"""
    s = pd.Series(prices)
    ema_short = s.ewm(span=short, adjust=False).mean()
    ema_long = s.ewm(span=long, adjust=False).mean()
    macd = ema_short - ema_long
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal

    base_key = f"{prefix}macd" if prefix else "macd"
    return {
        f"{base_key}_line": macd.iloc[-1] if not macd.empty else None,
        f"{base_key}_signal": macd_signal.iloc[-1] if not macd_signal.empty else None,
        f"{base_key}_histogram": macd_hist.iloc[-1] if not macd_hist.empty else None,
    }


def compute_all_timeframe_macd(prices):
    """모든 타임프레임별 MACD 계산"""
    results = {}
    if not prices or len(prices) < 10:
        return results

    # short, long, signal 파라미터는 각 시간대에 맞게 미세조정
    timeframes = {
        "1m_": (8, 17, 5),  # 초단타용
        "5m_": (10, 21, 7),  # 단기 스캘핑용
        "15m_": (12, 26, 9),  # 표준 MACD
        "1h_": (15, 30, 12),  # 스윙 기준
        "4h_": (20, 40, 15),  # 중기 추세
        "1d_": (12, 26, 9),  # 일봉 기준
    }

    for tf, (short, long, signal) in timeframes.items():
        if len(prices) >= long:  # 충분한 데이터가 있을 때만 계산
            results.update(compute_macd(prices, short, long, signal, tf))

    return results
