import os, asyncio
import numpy as np
from app.domain.quotes.quotes_ws_client import subscribe
from app.domain.quotes.indicators.rsi import compute_rsi
from app.domain.quotes.indicators.macd import compute_macd
from app.domain.quotes.indicators.bollinger import compute_bollinger
from app.domain.quotes.indicators.moving_average import compute_ema, compute_sma
from app.domain.quotes.indicators.stochastic import compute_stochastic
from app.domain.quotes.indicators.atr import compute_atr
from app.domain.quotes.indicators.volume import compute_rvol
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
    
    approval_key = redis_client.get("hanto:approval_key")
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
    if len(closes) >= 7:
        indicators["rsi7"] = to_native(compute_rsi(closes, 7).iloc[-1])
    if len(closes) >= 26:
        macd, sig, hist = compute_macd(closes)
        indicators["macd"] = {
            "line": to_native(macd.iloc[-1]),
            "signal": to_native(sig.iloc[-1]),
            "hist": to_native(hist.iloc[-1])
        }
    if len(closes) >= 20:
        ma, upper, lower = compute_bollinger(closes, 20, 2)
        indicators["bollinger"] = {
            "ma": to_native(ma.iloc[-1]),
            "upper": to_native(upper.iloc[-1]),
            "lower": to_native(lower.iloc[-1])
        }
        indicators["sma20"] = to_native(compute_sma(closes, 20).iloc[-1])
        indicators["ema8"] = to_native(compute_ema(closes, 8).iloc[-1])
        indicators["ema21"] = to_native(compute_ema(closes, 21).iloc[-1])
        indicators["ema50"] = to_native(compute_ema(closes, 50).iloc[-1])
    if len(closes) >= 14:
        stoch_k, stoch_d = compute_stochastic(highs, lows, closes)
        if stoch_k is not None and stoch_d is not None:
            indicators["stochastic"] = {
                "k": to_native(stoch_k.iloc[-1]),
                "d": to_native(stoch_d.iloc[-1])
            }
        atr = compute_atr(highs, lows, closes)
        indicators["atr14"] = to_native(atr.iloc[-1])
    if len(volumes) >= 20:
        indicators["rvol"] = to_native(compute_rvol(volumes, 20).iloc[-1])

    print(f"[Candle Closed] {candle}")
    print(f"[Indicators] {indicators}")
    print("-" * 60)
    
    send_candle(candle, indicators)
