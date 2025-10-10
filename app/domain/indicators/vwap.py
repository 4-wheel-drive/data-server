import pandas as pd


def compute_vwap(prices, volumes):
    """단일 VWAP 계산"""
    s_prices = pd.Series(prices)
    s_volumes = pd.Series(volumes)
    vwap = (s_prices * s_volumes).cumsum() / s_volumes.cumsum()
    return vwap


def compute_all_timeframe_vwap(prices, volumes):
    """
    모든 타임프레임별 VWAP 계산
    [1m, 5m, 15m, 1h, 4h, 1d]
    """
    results = {}
    timeframes = {
        "1m_": 1,
        "5m_": 5,
        "15m_": 15,
        "1h_": 60,
        "4h_": 240,
        "1d_": 390,  # 한국시장 기준 (9시~15시30분)
    }

    s_prices = pd.Series(prices)
    s_volumes = pd.Series(volumes)

    for prefix, window in timeframes.items():
        if len(s_prices) >= window:
            sub_prices = s_prices[-window:]
            sub_volumes = s_volumes[-window:]
            vwap = (sub_prices * sub_volumes).sum() / sub_volumes.sum()
            results[f"{prefix}vwap"] = vwap

    return results
