import os, asyncio
import numpy as np
from app.domain.minute_quotes.subscribe import subscribe
from app.config.redis_client import redis_client


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

    # approval_key = redis_client.get("kis:admin:approval-key")
    approval_key = "dddd"
    if not approval_key:
        raise RuntimeError("approval_key가 Redis에 없습니다")

    symbol = "068270"
    ws_task = asyncio.create_task(subscribe(symbol, approval_key))


async def stop_quotes():
    """웹소켓 구독 종료"""
    global ws_task
    if ws_task:
        ws_task.cancel()
        try:
            await ws_task
        except asyncio.CancelledError:
            pass
