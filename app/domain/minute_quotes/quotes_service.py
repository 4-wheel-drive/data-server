import os, asyncio
import numpy as np
from app.domain.minute_quotes.quotes_ws_client import subscribe
from app.domain.indicators.minute_rsi import compute_rsi
from app.domain.indicators.minute_macd import compute_macd
from app.domain.indicators.bollinger import compute_all_timeframe_bollinger
from app.domain.indicators.minute_moving_average import compute_ema, compute_sma
from app.domain.indicators.stochastic import compute_stochastic
from app.domain.indicators.atr import compute_atr
from app.domain.indicators.rvol import compute_all_timeframe_rvol
from app.domain.indicators.vwap import compute_all_timeframe_vwap  # ✅ 추가
from app.config.redis_client import redis_client
from app.config.kafka_producer import send_candle


candles = []
ws_task = None


def to_native(val):
    """numpy 타입 → 파이썬 기본 타입 변환"""
    if isinstance(val, (np.generic,)):
        return val.item()
    return val


async def start_quotes():
    """웹소켓 구독 시작"""
    global ws_task

    approval_key = redis_client.get("kis:admin:approval-key")
    if not approval_key:
        raise RuntimeError("approval_key가 Redis에 없습니다")

    symbol = "068270"
    ws_task = asyncio.create_task(subscribe(symbol, approval_key, on_candle))


async def stop_quotes():
    """웹소켓 구독 종료"""
    global ws_task
    if ws_task:
        ws_task.cancel()
        try:
            await ws_task
        except asyncio.CancelledError:
            pass


async def on_candle(candle):
    """1분봉 확정 시 호출"""
    candles.append(candle)
    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    volumes = [c["volume"] for c in candles]

    indicators = {}
    # ---------------- RSI ----------------
    if len(closes) >= 7:
        indicators["rsi7"] = to_native(compute_rsi(closes, 7).iloc[-1])

    # ---------------- MACD ----------------
    if len(closes) >= 26:
        macd, sig, hist = compute_macd(closes)
        indicators["macd"] = {
            "line": to_native(macd.iloc[-1]),
            "signal": to_native(sig.iloc[-1]),
            "hist": to_native(hist.iloc[-1]),
        }

    # ---------------- Bollinger Bands + MA ----------------
    if len(closes) >= 20:
        bb_values = compute_all_timeframe_bollinger(closes)
        indicators.update({k: to_native(v) for k, v in bb_values.items()})

        indicators["sma20"] = to_native(compute_sma(closes, 20).iloc[-1])
        indicators["ema8"] = to_native(compute_ema(closes, 8).iloc[-1])
        indicators["ema21"] = to_native(compute_ema(closes, 21).iloc[-1])
        indicators["ema50"] = to_native(compute_ema(closes, 50).iloc[-1])

    # ---------------- Stochastic + ATR ----------------
    if len(closes) >= 14:
        stoch_k, stoch_d = compute_stochastic(highs, lows, closes)
        if stoch_k is not None and stoch_d is not None:
            indicators["stochastic"] = {
                "k": to_native(stoch_k.iloc[-1]),
                "d": to_native(stoch_d.iloc[-1]),
            }
        atr = compute_atr(highs, lows, closes)
        indicators["atr14"] = to_native(atr.iloc[-1])

    # ---------------- RVOL ----------------
    if len(volumes) >= 20:
        rvol_values = compute_all_timeframe_rvol(volumes, 20)
        for key, value in rvol_values.items():
            indicators[key] = to_native(value)

    # ---------------- VWAP (NEW) ----------------
    if len(volumes) >= 5:  # 최소 5개 이상 봉 필요
        vwap_values = compute_all_timeframe_vwap(closes, volumes)
        for key, value in vwap_values.items():
            indicators[key] = to_native(value)

    # ---------------- Log & Kafka ----------------
    print(f"[Candle Closed] {candle}")
    print(f"[Indicators] {indicators}")
    print("-" * 60)

    send_candle(candle, indicators)
