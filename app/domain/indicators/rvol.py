import pandas as pd
import numpy as np


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


def compute_mono_timeframe_rvol(volumes, period=20):
    if len(volumes) < period:
        return {}

    avg_vol = np.mean(volumes[-period:])
    if avg_vol == 0:
        return {"rvol20": 1.0}

    return {"rvol20": float(round(volumes[-1] / avg_vol, 3))}
