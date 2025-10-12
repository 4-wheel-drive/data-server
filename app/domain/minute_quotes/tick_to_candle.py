from datetime import datetime, timedelta
from collections import defaultdict
from app.domain.minute_quotes.candles.candle_engine import update_candle

timeframes = {
    "1m": timedelta(minutes=1),
    "5m": timedelta(minutes=5),
    "15m": timedelta(minutes=15),
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
}

# 종목별 → 타임프레임별 → 봉 데이터 리스트
candles_buffer = defaultdict(lambda: defaultdict(list))


def on_tick(symbol: str, price: float, volume: int, tick_time: str):
    """
    실시간 체결(Tick) 데이터 수신 시 처리
    - timeframe별 봉 누적 버퍼 업데이트
    - 봉이 확정되면 update_candle() 호출
    """
    try:
        now = datetime.strptime(tick_time, "%H%M%S")

        for tf, delta in timeframes.items():
            buffer = candles_buffer[symbol][tf]

            if not buffer or now - buffer[-1]["timestamp"] >= delta:
                buffer.append(
                    {
                        "timestamp": now,
                        "open": price,
                        "high": price,
                        "low": price,
                        "close": price,
                        "volume": volume,
                    }
                )

            else:
                candle = buffer[-1]
                candle["high"] = max(candle["high"], price)
                candle["low"] = min(candle["low"], price)
                candle["close"] = price
                candle["volume"] += volume

            if len(buffer) > 1:
                try:
                    update_candle(symbol, tf, buffer[:-1])
                except Exception as e:
                    print(f"[WARN] update_candle 실패 ({symbol}, {tf}) → {e}")

    except Exception as e:
        print(f"[ERROR] on_tick({symbol}) 처리 중 예외 발생 → {e}")
