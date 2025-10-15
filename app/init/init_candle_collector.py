# app/domain/minute_quotes/collect_candles_full_v5_multi_stock.py
import os
import time
import requests
import datetime
from collections import defaultdict
from app.infra.redis_client import redis_client
from app.domain.minute_quotes.candles.services.candle_storage import push_candle
from dotenv import load_dotenv

# -----------------------------
# 종목 리스트
# -----------------------------
STOCKS = [
    {"code": "005930", "name": "삼성전자"},
    {"code": "000660", "name": "SK하이닉스"},
    {"code": "035420", "name": "NAVER"},
    {"code": "005380", "name": "현대자동차"},
    {"code": "051910", "name": "LG화학"},
    {"code": "006400", "name": "삼성SDI"},
    {"code": "035720", "name": "카카오"},
    {"code": "000270", "name": "기아"},
    {"code": "068270", "name": "셀트리온"},
    {"code": "207940", "name": "삼성바이오로직스"},
    {"code": "005490", "name": "POSCO홀딩스"},
    {"code": "066570", "name": "LG전자"},
    {"code": "012330", "name": "현대모비스"},
    {"code": "000810", "name": "삼성화재"},
    {"code": "015760", "name": "한국전력"},
    {"code": "259960", "name": "크래프톤"},
    {"code": "086520", "name": "에코프로"},
    {"code": "247540", "name": "에코프로비엠"},
    {"code": "034730", "name": "SK"},
    {"code": "018260", "name": "삼성SDS"},
]

# -----------------------------
# 기본 설정
# -----------------------------
BASE_URL = "https://openapi.koreainvestment.com:9443"
TOKEN_URL = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
PATH = "/uapi/domestic-stock/v1/quotations/inquire-time-dailychartprice"

load_dotenv()

APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
ACCESS_TOKEN_TTL = 24 * 60 * 60
DAYS_TO_FETCH = 200


# -----------------------------
# Token 관리
# -----------------------------
def get_token():
    token = redis_client.get("kis:user:1:access-token")
    if token:
        return token
    res = requests.post(
        TOKEN_URL,
        headers={"content-type": "application/json"},
        json={
            "grant_type": "client_credentials",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET,
        },
    )
    res.raise_for_status()
    data = res.json()
    token = data.get("access_token")
    redis_client.setex("kis:user:1:access-token", ACCESS_TOKEN_TTL, token)
    return token


# -----------------------------
# 안정 GET
# -----------------------------
def safe_get(url, headers, params, retries=3, sleep_sec=1.0):
    for i in range(retries):
        try:
            res = requests.get(url, headers=headers, params=params, timeout=8)
            if res.ok:
                return res
            print(f"⚠️ 요청 실패 {res.status_code} (시도 {i+1}/{retries})")
        except Exception as e:
            print(f"❌ 네트워크 오류: {e}")
        time.sleep(sleep_sec)
    raise RuntimeError("🚨 최대 재시도 초과")


# -----------------------------
# 하루치 분봉 조회 (09:00~15:30)
# -----------------------------
def get_one_day_candles(symbol: str, date: str):
    token = get_token()
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST03010230",
        "custtype": "P",
    }

    all_candles = []
    for hour in ["090000", "110000", "130000", "153000"]:
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": symbol,
            "FID_INPUT_DATE_1": date,
            "FID_INPUT_HOUR_1": hour,
            "FID_PW_DATA_INCU_YN": "Y",
            "FID_FAKE_TICK_INCU_YN": "",
        }
        res = safe_get(BASE_URL + PATH, headers=headers, params=params)
        data = res.json().get("output2", [])
        for d in data:
            try:
                t = f"{d['stck_bsop_date']}{d['stck_cntg_hour'][:4]}"
                all_candles.append(
                    {
                        "t": t,
                        "o": float(d["stck_oprc"]),
                        "h": float(d["stck_hgpr"]),
                        "l": float(d["stck_lwpr"]),
                        "c": float(d["stck_prpr"]),
                        "v": int(d["cntg_vol"]),
                    }
                )
            except Exception:
                continue
        time.sleep(0.4)

    unique = {c["t"]: c for c in all_candles}
    sorted_candles = sorted(unique.values(), key=lambda x: x["t"])
    processed = postprocess_candles(sorted_candles)
    return processed


# -----------------------------
# 누적 거래량 / 거래대금 / 체결강도 계산
# -----------------------------
def postprocess_candles(sorted_candles):
    cumulative_vol, cumulative_val, prev_close = 0, 0, None
    processed = []
    for c in sorted_candles:
        cumulative_vol += c["v"]
        cumulative_val += c["c"] * c["v"]
        tick_strength = (
            round(((c["c"] - prev_close) / prev_close) * 100, 4) if prev_close else 0.0
        )
        processed.append(
            {
                **c,
                "cumulative_volume": cumulative_vol,
                "cumulative_value": cumulative_val,
                "tick_strength": tick_strength,
            }
        )
        prev_close = c["c"]
    return processed


# -----------------------------
# 상위 봉 집계
# -----------------------------
def aggregate_candles(candles, interval_minutes):
    buckets = defaultdict(list)
    for c in candles:
        t = datetime.datetime.strptime(c["t"], "%Y%m%d%H%M")
        if t.hour == 15 and t.minute > 30:
            continue
        block = t.replace(
            minute=(t.minute // interval_minutes) * interval_minutes, second=0
        )
        buckets[block].append(c)

    result = []
    for block_time, group in sorted(buckets.items()):
        o, h, l, c_ = (
            group[0]["o"],
            max(x["h"] for x in group),
            min(x["l"] for x in group),
            group[-1]["c"],
        )
        v = sum(x["v"] for x in group)
        cv, val = group[-1]["cumulative_volume"], group[-1]["cumulative_value"]
        tick = sum(x["tick_strength"] for x in group) / len(group)
        result.append(
            {
                "t": block_time.strftime("%Y%m%d%H%M"),
                "o": o,
                "h": h,
                "l": l,
                "c": c_,
                "v": v,
                "cumulative_volume": cv,
                "cumulative_value": val,
                "tick_strength": round(tick, 4),
            }
        )
    return result


# -----------------------------
# 한국형 4시간봉 (오전/오후)
# -----------------------------
def aggregate_4h_korea(candles):
    buckets = defaultdict(list)
    for c in candles:
        t = datetime.datetime.strptime(c["t"], "%Y%m%d%H%M")
        block = (
            datetime.datetime(t.year, t.month, t.day, 9, 0)
            if t.hour < 13
            else datetime.datetime(t.year, t.month, t.day, 13, 0)
        )
        buckets[block].append(c)

    result = []
    for block_time, group in sorted(buckets.items()):
        o, h, l, c_ = (
            group[0]["o"],
            max(x["h"] for x in group),
            min(x["l"] for x in group),
            group[-1]["c"],
        )
        v = sum(x["v"] for x in group)
        cv, val = group[-1]["cumulative_volume"], group[-1]["cumulative_value"]
        tick = sum(x["tick_strength"] for x in group) / len(group)
        result.append(
            {
                "t": block_time.strftime("%Y%m%d%H%M"),
                "o": o,
                "h": h,
                "l": l,
                "c": c_,
                "v": v,
                "cumulative_volume": cv,
                "cumulative_value": val,
                "tick_strength": round(tick, 4),
            }
        )
    return result


# -----------------------------
# 메인 (모든 종목 수집)
# -----------------------------
def collect_stock(symbol: str, name: str):
    print(f"\n🚀 [{symbol}] {name} 200일치 분봉 수집 시작", flush=True)

    all_candles = []
    now = datetime.datetime.now()
    for i in range(DAYS_TO_FETCH):
        date = (now - datetime.timedelta(days=i + 1)).strftime("%Y%m%d")
        if datetime.datetime.strptime(date, "%Y%m%d").weekday() >= 5:
            continue
        candles = get_one_day_candles(symbol, date)
        if candles:
            all_candles.extend(candles)
            print(f"📅 {symbol} {date}: 누적 {len(all_candles)}개")

    five_min = aggregate_candles(all_candles, 5)
    fifteen_min = aggregate_candles(all_candles, 15)
    one_hour = aggregate_candles(all_candles, 60)
    four_hour = aggregate_4h_korea(all_candles)

    print(
        f"[{symbol}] 1m:{len(all_candles)} / 5m:{len(five_min)} / 15m:{len(fifteen_min)} / 1h:{len(one_hour)} / 4h:{len(four_hour)}"
    )

    for tf, data in {
        "1m": all_candles[-200:],
        "5m": five_min[-200:],
        "15m": fifteen_min[-200:],
        "1h": one_hour[-200:],
        "4h": four_hour[-200:],
    }.items():
        for c in data:
            push_candle(symbol, tf, c)
        print(f"✅ [{symbol}] {tf}: {len(data)}개 저장 완료")

    print(f"🏁 [{symbol}] {name} 완료 ✅")


def main():
    for stock in STOCKS:
        try:
            collect_stock(stock["code"], stock["name"])
        except Exception as e:
            print(f"❌ [{stock['code']}] {stock['name']} 오류: {e}")
            continue
    print("｢모든 종목 수집 완료｣")


# -----------------------------
# 실행 엔트리포인트
# -----------------------------
if __name__ == "__main__":
    print("｢실행 시작｣", flush=True)
    try:
        main()
    except Exception as e:
        print(f"main 실행 중 오류: {e}", flush=True)
