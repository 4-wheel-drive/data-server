import websockets, json
from app.domain.qutoes.candles.tick_to_minute import update_candle

async def subscribe(symbol, approval_key, on_candle):
    async with websockets.connect("ws://ops.koreainvestment.com:31000") as ws:
        sub_msg = {
            "header": {"approval_key": approval_key, "custtype": "P", "tr_type": "1"},
            "body": {"input": {"tr_id": "H0STCNT0", "tr_key": symbol}}
        }
        await ws.send(json.dumps(sub_msg))

        while True:
            data = await ws.recv()
            _, _, _, payload = data.split("|", 3)
            fields = payload.split("^")
            price = int(fields[2])
            volume = int(fields[12])
            tick_time = fields[1]

            closed_candle = update_candle(price, volume, tick_time)
            if closed_candle:
                await on_candle(closed_candle)
