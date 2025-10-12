from app.domain.indicators.moving_average import compute_mono_timeframe_ma
from app.domain.indicators.rsi import compute_mono_timeframe_rsi
from app.domain.indicators.macd import compute_mono_timeframe_macd
from app.domain.indicators.bollinger import compute_mono_timeframe_bollinger
from app.domain.indicators.vwap import compute_mono_timeframe_vwap
from app.domain.indicators.rvol import compute_mono_timeframe_rvol
from app.domain.indicators.cumulative import compute_cumulative_values
from app.config.redis_client import redis_client
import json

SUPPORTED_TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h"]


def update_candle(symbol, timeframe, candles):
    """새 봉 확정 시 (timeframe별) 전체 지표 계산"""
    if timeframe not in SUPPORTED_TIMEFRAMES:
        return None

    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    volumes = [c["volume"] for c in candles]
    latest = candles[-1]

    # 기본 OHLC 데이터
    data = {
        "open": latest["open"],
        "high": latest["high"],
        "low": latest["low"],
        "close": latest["close"],
    }

    # ==========================
    # 지표 계산 (모두 단일 타임프레임 버전)
    # ==========================
    data.update(compute_mono_timeframe_ma(closes, timeframe))  # SMA, EMA
    data.update(compute_mono_timeframe_rsi(closes, timeframe))  # RSI 7, 14, 21
    data.update(compute_mono_timeframe_macd(closes))  # MACD
    data.update(compute_mono_timeframe_bollinger(closes))  # Bollinger Bands
    data.update(compute_mono_timeframe_vwap(closes, volumes))  # VWAP
    data.update(compute_mono_timeframe_rvol(volumes))  # RVOL
    data.update(compute_cumulative_values(candles))  # 누적 거래량/대금

    # ==========================
    # 캐시 업데이트 및 반환
    # ==========================
    key = f"market:{symbol}:{timeframe}"
    redis_client.set(key, json.dumps(data))

    return {symbol: {timeframe: data}}
