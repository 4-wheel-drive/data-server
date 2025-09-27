import asyncio
import websockets
import json
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

QUTOES_URL = "ws://ops.koreainvestment.com:31000"
APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")

# ===== 전역 상태 =====
close_series = []
current_candle = None
prev_minute = None

# ===== 보조지표 계산기 =====
def compute_rsi(prices, period=14):
    s = pd.Series(prices)
    delta = s.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    roll_up = up.ewm(span=period).mean()
    roll_down = down.ewm(span=period).mean()
    rs = roll_up / roll_down
    return 100 - (100 / (1 + rs))

def compute_macd(prices, short=12, long=26, signal=9):
    s = pd.Series(prices)
    ema_short = s.ewm(span=short, adjust=False).mean()
    ema_long = s.ewm(span=long, adjust=False).mean()
    macd = ema_short - ema_long
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal
    return macd, macd_signal, macd_hist

def compute_bollinger(prices, window=20, num_std=2):
    s = pd.Series(prices)
    ma = s.rolling(window).mean()
    std = s.rolling(window).std()
    upper = ma + num_std * std
    lower = ma - num_std * std
    return ma, upper, lower

def compute_sma(prices, window=20):
    return pd.Series(prices).rolling(window).mean()

def compute_ema(prices, window=20):
    return pd.Series(prices).ewm(span=window, adjust=False).mean()

# ===== 틱 처리 =====
async def handle_tick(data: str):
    global current_candle, prev_minute, close_series

    if "|" not in data or "^" not in data:
        return

    try:
        _, tr_id, _, payload = data.split("|", 3)
    except ValueError:
        return

    fields = payload.split("^")
    if len(fields) < 3:
        return

    try:
        price = int(fields[2])  # 현재가
        tick_time = fields[1]   # HHMMSS
    except ValueError:
        return

    minute_key = tick_time[:4]  # ex: "0906"

    if prev_minute is None:
        prev_minute = minute_key
        current_candle = {"open": price, "high": price, "low": price, "close": price}
        return

    if minute_key != prev_minute:
        # ===== 봉 확정 =====
        close_series.append(current_candle["close"])
        print(f"[확정된 봉]({prev_minute}): {current_candle}")
        print(f"[Close Series]({len(close_series)}): {close_series[-5:]}")  # 최근 5개만 표시

        # ===== 지표 계산 =====
        if len(close_series) >= 14:
            rsi = compute_rsi(close_series, 14).iloc[-1]
            print(f"[RSI(14)]: {rsi:.2f}")

        if len(close_series) >= 26:  # MACD 최소 26봉 필요
            macd, signal, hist = compute_macd(close_series)
            print(f"[MACD]: {macd.iloc[-1]:.2f}, Signal: {signal.iloc[-1]:.2f}, Hist: {hist.iloc[-1]:.2f}")

        if len(close_series) >= 20:
            ma, upper, lower = compute_bollinger(close_series, 20, 2)
            print(f"[Bollinger]: MA={ma.iloc[-1]:.2f}, Upper={upper.iloc[-1]:.2f}, Lower={lower.iloc[-1]:.2f}")

            sma20 = compute_sma(close_series, 20).iloc[-1]
            ema20 = compute_ema(close_series, 20).iloc[-1]
            print(f"[SMA20]: {sma20:.2f}, [EMA20]: {ema20:.2f}")

        print("-" * 50)

        # 새 봉 시작
        prev_minute = minute_key
        current_candle = {"open": price, "high": price, "low": price, "close": price}
    else:
        # ===== 현재 봉 갱신 =====
        current_candle["high"] = max(current_candle["high"], price)
        current_candle["low"] = min(current_candle["low"], price)
        current_candle["close"] = price

# ===== WS 구독 =====
async def subscribe(symbol: str, approval_key: str):
    async with websockets.connect(QUTOES_URL, ping_interval=20, ping_timeout=20) as ws:
        # 구독``
        sub_msg = {
            "header": {
                "approval_key": approval_key,
                "custtype": "P",
                "tr_type": "1",  # 구독
                "content-type": "utf-8"
            },
            "body": {
                "input": {
                    "tr_id": "H0STCNT0",
                    "tr_key": symbol
                }
            }
        }

        # 해제
        unsub_msg = {
            "header": {
                "approval_key": approval_key,
                "custtype": "P",
                "tr_type": "2",  # 구독 해제
                "content-type": "utf-8"
            },
            "body": {
                "input": {
                    "tr_id": "H0STCNT0",
                    "tr_key": symbol
                }
            }
        }

        try:
            # 구독 요청
            await ws.send(json.dumps(sub_msg))
            print(f"[1] {symbol} 구독 시작")

            # 데이터 수신
            while True:
                data = await ws.recv()
                await handle_tick(data)

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"서버가 연결 종료: {e}")
        except Exception as e:
            print(f"예기치 못한 에러: {e}")
        finally:
            try:
                await ws.send(json.dumps(unsub_msg))
                print(f"{symbol} 구독 해제 완료")
            except:
                print("구독 해제 중 연결이 이미 닫힘")
            await ws.close()


    """
        테스트용 함수
    """
if __name__ == "__main__":
    asyncio.run(subscribe("005930", "278f08a8-da6f-403e-a00b-064fc12d3967"))
