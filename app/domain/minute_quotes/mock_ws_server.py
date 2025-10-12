import asyncio
import websockets
import random
import datetime


async def handler(ws):
    await ws.recv()  # 구독 무시
    while True:
        symbol = "005930"
        tick_time = datetime.datetime.now().strftime("%H%M%S")
        price = random.randint(64000, 66000)
        change_rate = round(random.uniform(-2.0, 2.0), 2)
        volume = random.randint(100, 500)
        cumulative_vol = random.randint(200000, 400000)
        cumulative_value = random.randint(6_000_000_000, 10_000_000_000)
        strength = round(random.uniform(90.0, 110.0), 2)

        fields = ["0"] * 70
        fields[1] = tick_time  # STCK_CNTG_HOUR
        fields[2] = str(price)  # STCK_PRPR
        fields[3] = "2"  # PRDY_VRSS_SIGN (상승)
        fields[4] = str(random.randint(100, 500))  # PRDY_VRSS
        fields[5] = str(change_rate)  # PRDY_CTRT (%)
        fields[6] = "65000"  # WGHN_AVRG_STCK_PRC
        fields[7] = "64500"  # STCK_OPRC
        fields[8] = "66000"  # STCK_HGPR
        fields[9] = "64000"  # STCK_LWPR
        fields[10] = "66100"  # ASKP1
        fields[11] = "65900"  # BIDP1
        fields[12] = str(volume)  # CNTG_VOL
        fields[13] = str(cumulative_vol)  # ACML_VOL
        fields[14] = str(cumulative_value)  # ACML_TR_PBMN
        fields[15] = str(strength)  # CTTR

        payload = "^".join(fields)
        msg = f"0|H0STCNT0|{symbol}|{payload}"

        await ws.send(msg)
        print(f"📤 mock tick {symbol}: {price} ({change_rate}%) 강도={strength}")
        await asyncio.sleep(0.4)


async def main():
    server = await websockets.serve(handler, "localhost", 31000)
    print("✅ mock 시세 서버 시작됨 (^, | 포맷 — 실제 한투 순서 반영)")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
