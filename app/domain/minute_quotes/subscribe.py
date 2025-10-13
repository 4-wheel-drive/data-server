import asyncio
import websockets
import json
from app.infra.redis_client import redis_client
from app.domain.minute_quotes.tick_to_candle import on_tick

WS_URL = "ws://ops.koreainvestment.com:21000"  # 실서버


async def start_multi_subscribe(symbols):
    approval_key = redis_client.get("kis:admin:approval-key")
    if not approval_key:
        raise RuntimeError("approval_key가 Redis에 없습니다 (실서버 키 필요)")

    print("실서버 WebSocket 실시간 구독 시작", flush=True)

    while True:
        try:
            async with websockets.connect(
                WS_URL, ping_interval=25, ping_timeout=15
            ) as ws:
                print("실서버 연결 성공", flush=True)

                # 구독 요청
                for symbol in symbols:
                    msg = {
                        "header": {
                            "approval_key": approval_key,
                            "custtype": "P",
                            "tr_type": "1",
                            "content-type": "utf-8",
                        },
                        "body": {"input": {"tr_id": "H0STCNT0", "tr_key": symbol}},
                    }
                    await ws.send(json.dumps(msg))
                    print(f"📤 [{symbol}] 구독 요청 전송 완료", flush=True)
                    await asyncio.sleep(0.25)

                print("모든 종목 구독 완료 — tick 대기 중...", flush=True)

                # 수신 루프
                while True:
                    raw = await ws.recv()

                    if raw.startswith("{"):
                        print(f"서버 응답: {raw}", flush=True)
                        continue

                    try:
                        _, tr_id, tr_key, payload = raw.split("|", 3)
                        if tr_id != "H0STCNT0":
                            continue

                        fields = payload.split("^")
                        symbol = fields[0]
                        tick_time = fields[1]
                        price = float(fields[2])
                        cumulative_volume = int(fields[8]) if fields[8] else 0
                        cumulative_value = int(fields[9]) if fields[9] else 0
                        tick_strength = float(fields[13]) if fields[13] else None
                        change_rate = float(fields[5]) if fields[5] else None
                        volume = int(fields[8]) if fields[8] else 0

                        print(
                            f"📊 [{symbol}] {tick_time} | 가격={price:,.0f} | 체결강도={tick_strength} | 등락률={change_rate}",
                            flush=True,
                        )

                        on_tick(
                            symbol=symbol,
                            price=price,
                            volume=volume,
                            tick_time=tick_time,
                            cumulative_volume=cumulative_volume,
                            cumulative_value=cumulative_value,
                            tick_strength=tick_strength,
                            change_rate=change_rate,
                        )

                    except Exception as e:
                        print(f"[PARSE ERROR] {e} / raw={raw[:120]!r}", flush=True)

        except Exception as e:
            print(f"WebSocket 연결 끊김 ({e}) → 5초 후 재시도", flush=True)
            await asyncio.sleep(5)
