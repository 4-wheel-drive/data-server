import asyncio, random
from datetime import datetime, timedelta
from app.domain.quotes.candles.tick_to_minute import update_candle

async def mock_subscribe(symbol, approval_key, on_candle, interval=0.05):
    """
    무한히 틱 데이터를 생성해서 on_candle 콜백으로 전달.
    interval: 틱 사이 간격(초)
    """
    price = 84200
    volume_cum = 0
    value_cum = 0.0
    t = datetime.strptime("090000", "%H%M%S")
    i = 0

    while True:  # 무한 루프
        # 가격 랜덤 변동
        price += random.choice([-100, -50, 0, 50, 100])
        volume = random.randint(10, 500)
        trade_value = price * volume

        # 누적값 갱신
        volume_cum += volume
        value_cum += trade_value
        vwap = value_cum / volume_cum

        tick_time = (t + timedelta(seconds=i)).strftime("%H%M%S")

        # API 메시지 포맷 목킹
        raw = (
            f"0|H0STCNT0|001|{symbol}^{tick_time}^{price}^5^0^0^{vwap:.2f}^"
            f"{price-100}^{price+100}^{price-200}^{price}^{price}^"
            f"{volume}^{volume_cum}^{trade_value}^10^20^5^50.0^"
            f"100^200^1^0.3^32.0^{tick_time}^5^0^{tick_time}^5^0^{tick_time}^2^0^"
            f"{datetime.today().strftime('%Y%m%d')}^20^N^0^0^0^0^0^0^0^0^^{price}"
        )

        # 틱 → 분봉 변환
        _, _, _, payload = raw.split("|", 3)
        fields = payload.split("^")
        closed_candle = update_candle(int(fields[2]), int(fields[12]), fields[1])
        if closed_candle:
            await on_candle(closed_candle)

        await asyncio.sleep(interval)
        i += 1
