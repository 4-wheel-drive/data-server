import random
from datetime import datetime, timedelta

def generate_mock_ticks(symbol="005930", start_price=84200, start_time="090000", n_ticks=100):
    ticks = []
    price = start_price
    volume_cum = 0
    value_cum = 0.0

    # 시작 시간 datetime 변환
    t = datetime.strptime(start_time, "%H%M%S")

    for i in range(n_ticks):
        # 가격 랜덤 변동
        price += random.choice([-50, 0, 50, 100, -100])
        volume = random.randint(10, 500)  # 랜덤 거래량
        trade_value = price * volume

        # 누적값 갱신
        volume_cum += volume
        value_cum += trade_value
        vwap = value_cum / volume_cum

        # 체결 시간 (초 단위 증가)
        tick_time = (t + timedelta(seconds=i)).strftime("%H%M%S")

        # 실제 API 포맷 흉내
        msg = (
            f"0|H0STCNT0|001|"
            f"{symbol}^{tick_time}^{price}^5^0^0^{vwap:.2f}^"
            f"{price-100}^{price+100}^{price-200}^{price}^{price}^"
            f"{volume}^{volume_cum}^{trade_value}^10^20^5^50.0^"
            f"100^200^1^0.3^32.0^{tick_time}^5^0^{tick_time}^5^0^{tick_time}^2^0^"
            f"{datetime.today().strftime('%Y%m%d')}^20^N^0^0^0^0^0^0^0^0^^{price}"
        )
        ticks.append(msg)

    return ticks

# 사용 예시
mock_data = generate_mock_ticks(n_ticks=10)
for line in mock_data:
    print(line)
