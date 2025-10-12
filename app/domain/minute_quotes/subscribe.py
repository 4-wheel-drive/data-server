import websockets
import json
from datetime import datetime
from app.infra.redis_client import redis_client
from app.domain.minute_quotes.tick_to_candle import on_tick


def safe_float(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def safe_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


async def subscribe(symbol: str, approval_key: str):
    async with websockets.connect("ws://localhost:31000") as ws:
        sub_msg = {
            "header": {
                "approval_key": approval_key,
                "custtype": "P",
                "tr_type": "1",
                "content-type": "utf-8",
            },
            "body": {"input": {"tr_id": "H0STCNT0", "tr_key": symbol}},
        }

        await ws.send(json.dumps(sub_msg))
        print(f"구독 요청 전송 완료: {symbol}")

        while True:
            raw = await ws.recv()
            if raw.startswith("{"):
                continue

            try:
                _, _, _, payload = raw.split("|", 3)
                fields = payload.split("^")

                tick_time = fields[1]
                price = safe_float(fields[2])
                change_rate = safe_float(fields[5])
                volume = safe_int(fields[12])
                cumulative_volume = safe_int(fields[13])
                cumulative_value = safe_int(fields[14])
                tick_strength = safe_float(fields[15])

                summary = {
                    "symbol": symbol,
                    "tick_time": tick_time,
                    "price": price,
                    "change_rate": change_rate,
                    "volume": volume,
                    "cumulative_volume": cumulative_volume,
                    "cumulative_value": cumulative_value,
                    "tick_strength": tick_strength,
                }

                redis_client.set(f"market:{symbol}:tick", json.dumps(summary))

                # 인자 전체 전달
                on_tick(
                    symbol,
                    price,
                    volume,
                    tick_time,
                    cumulative_volume=cumulative_volume,
                    cumulative_value=cumulative_value,
                    tick_strength=tick_strength,
                    change_rate=change_rate,
                )

                print(
                    f"{symbol} {tick_time} | "
                    f"현재가={price:,.0f} | "
                    f"등락={change_rate:.2f}% | "
                    f"체결강도={tick_strength:.2f}"
                )

            except Exception as e:
                print("[PARSE ERROR]", e)
