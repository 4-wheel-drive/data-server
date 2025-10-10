import pandas as pd


def compute_rvol(volumes, period=20):
    """상대 거래량 (단일 period 기준)"""
    s = pd.Series(volumes)
    vol_ma = s.rolling(window=period).mean()
    return s / vol_ma


def compute_all_timeframe_rvol(volumes, period=20):
    """
    타임프레임별 RVOL 계산
    [1m, 5m, 15m, 1h, 4h, 1d]
    """
    results = {}
    timeframes = ["1m_", "5m_", "15m_", "1h_", "4h_", "1d_"]

    s = pd.Series(volumes)
    vol_ma = s.rolling(window=period).mean()
    rvol = s / vol_ma

    if len(s) < period:
        return results

    for tf in timeframes:
        results[f"{tf}rvol"] = rvol.iloc[-1]

    return results
