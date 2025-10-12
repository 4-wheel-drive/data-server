import websockets
import json
from app.config.redis_client import redis_client
from app.domain.minute_quotes.schemes.tick_response import ResponseBody


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

                body = ResponseBody(*fields[: len(ResponseBody.__dataclass_fields__)])

                key_raw = f"market:{symbol}:tick_raw"
                redis_client.set(key_raw, json.dumps(body.__dict__))

                key_summary = f"market:{symbol}:tick"
                summary = {
                    "symbol": symbol,
                    "tick_time": body.STCK_CNTG_HOUR,
                    "price": float(body.STCK_PRPR),
                    "change_rate": float(body.PRDY_CTRT),
                    "volume": int(body.CNTG_VOL),
                    "cumulative_volume": int(body.ACML_VOL),
                    "cumulative_value": int(body.ACML_TR_PBMN),
                    "tick_strength": float(body.CTTR),
                }
                redis_client.set(key_summary, json.dumps(summary))

                print(
                    f"{symbol} {summary['tick_time']} | {summary['price']} | 강도={summary['tick_strength']}"
                )

            except Exception as e:
                print("[PARSE ERROR]", e, raw)
