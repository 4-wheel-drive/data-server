import websockets, json
from app.domain.quotes.candles.tick_to_minute import update_candle

async def subscribe(symbol, approval_key, on_candle):
    async with websockets.connect("ws://ops.koreainvestment.com:31000") as ws:
        sub_msg = {
            "header": {"approval_key": approval_key, "custtype": "P", "tr_type": "1"},
            "body": {"input": {"tr_id": "H0STCNT0", "tr_key": symbol}}
        }
        await ws.send(json.dumps(sub_msg))

        while True:
            try:
                data = await ws.recv()
                
                # 데이터가 비어있거나 예상 형식이 아닌 경우 건너뛰기
                if not data or "|" not in data:
                    continue
                    
                parts = data.split("|", 3)
                if len(parts) < 4:
                    continue
                    
                _, _, _, payload = parts
                
                if not payload or "^" not in payload:
                    continue
                    
                fields = payload.split("^")
                if len(fields) < 13:
                    continue
                    
                price = int(fields[2])
                volume = int(fields[12])
                tick_time = fields[1]

                closed_candle = update_candle(price, volume, tick_time)
                if closed_candle:
                    await on_candle(closed_candle)
                    
            except websockets.exceptions.ConnectionClosed:
                # WebSocket 연결이 끊어진 경우 정상 종료
                break
            except (ValueError, IndexError) as e:
                # 데이터 파싱 에러 시 해당 데이터 건너뛰기
                print(f"WebSocket 데이터 파싱 에러 (건너뛰기): {e}")
                continue
            except Exception as e:
                # 기타 예외 발생 시 로그 출력 후 종료
                print(f"WebSocket 처리 중 예외 발생: {e}")
                break
