from datetime import datetime
from typing import Dict, Tuple
from .candle_storage import push_candle


class CandleBuilder:
    """Tick을 받아 1m 봉을 생성하는 클래스"""

    def __init__(self):
        self.buffer: Dict[Tuple[str, datetime], dict] = {}

    def update_tick(self, ticker: str, price: float, volume: float, ts: datetime):
        minute = ts.replace(second=0, microsecond=0)
        key = (ticker, minute)

        if key not in self.buffer:
            self.buffer[key] = {
                "t": minute.isoformat(),
                "o": price,
                "h": price,
                "l": price,
                "c": price,
                "v": volume,
            }
        else:
            c = self.buffer[key]
            c["h"] = max(c["h"], price)
            c["l"] = min(c["l"], price)
            c["c"] = price
            c["v"] += volume

    def flush_completed_candles(self, ticker: str, now: datetime):
        """완성된 1m 봉을 Redis에 저장"""
        cutoff = now.replace(second=0, microsecond=0)
        finished = [k for k in self.buffer.keys() if k[0] == ticker and k[1] < cutoff]

        for key in finished:
            _, minute = key
            candle = self.buffer.pop(key)
            push_candle(ticker, "1m", candle)
