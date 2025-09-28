candles_1m = []
current_candle = None
prev_minute = None

def update_candle(price: float, volume: int, tick_time: str):
    """
    틱 데이터를 받아 1분봉 확정 시 반환
    tick_time: HHMMSS (예: "093015")
    """
    global current_candle, prev_minute
    minute_key = tick_time[:4]

    if prev_minute is None:
        prev_minute = minute_key
        current_candle = {"open": price, "high": price, "low": price,
                          "close": price, "volume": volume}
        return None

    if minute_key != prev_minute:
        closed = current_candle
        candles_1m.append(closed)
        prev_minute = minute_key
        current_candle = {"open": price, "high": price, "low": price,
                          "close": price, "volume": volume}
        return closed
    else:
        current_candle["high"] = max(current_candle["high"], price)
        current_candle["low"] = min(current_candle["low"], price)
        current_candle["close"] = price
        current_candle["volume"] += volume
        return None
