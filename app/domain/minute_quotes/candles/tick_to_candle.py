from datetime import datetime

TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h"]

current_candles = {tf: None for tf in TIMEFRAMES}
prev_keys = {tf: None for tf in TIMEFRAMES}
candles = {tf: [] for tf in TIMEFRAMES}


def _get_time_key(dt: datetime, tf: str):
    if tf == "1m":
        return dt.replace(second=0, microsecond=0)
    elif tf == "5m":
        return dt.replace(minute=(dt.minute // 5) * 5, second=0, microsecond=0)
    elif tf == "15m":
        return dt.replace(minute=(dt.minute // 15) * 15, second=0, microsecond=0)
    elif tf == "1h":
        return dt.replace(minute=0, second=0, microsecond=0)
    elif tf == "4h":
        return dt.replace(hour=(dt.hour // 4) * 4, minute=0, second=0, microsecond=0)


def _init_candle(price: float, volume: int):
    return {
        "open": price,
        "high": price,
        "low": price,
        "close": price,
        "volume": volume,
        "vwap_num": price * volume,
        "vwap_den": volume,
    }


def _finalize_candle(c):
    c = c.copy()
    c["vwap"] = c["vwap_num"] / c["vwap_den"] if c["vwap_den"] > 0 else c["close"]
    return c


def update_all_candles(price: float, volume: int, tick_time: str):
    dt = datetime.strptime(tick_time, "%H%M%S")
    closed_candles = {}

    for tf in TIMEFRAMES:
        key = _get_time_key(dt, tf)

        if prev_keys[tf] is None:
            prev_keys[tf] = key
            current_candles[tf] = _init_candle(price, volume)
            continue

        if key != prev_keys[tf]:
            finalized = _finalize_candle(current_candles[tf])
            finalized["timeframe"] = tf
            finalized["timestamp"] = prev_keys[tf]
            candles[tf].append(finalized)
            closed_candles[tf] = finalized

            prev_keys[tf] = key
            current_candles[tf] = _init_candle(price, volume)
        else:
            c = current_candles[tf]
            c["high"] = max(c["high"], price)
            c["low"] = min(c["low"], price)
            c["close"] = price
            c["volume"] += volume
            c["vwap_num"] += price * volume
            c["vwap_den"] += volume

    return closed_candles
