import os
import sys
import time
import json
import random
import datetime as dt
import pymysql
import requests
import redis
from dotenv import load_dotenv

# ========== 설정 ==========
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASSWORD", "admin1024")
DB_NAME = os.getenv("DB_NAME", "modular1")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PW = os.getenv("REDIS_PASSWORD", "admin1024")

APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")

BASE_URL = "https://openapi.koreainvestment.com:9443"
QUOTE_PATH = "/uapi/domestic-stock/v1/quotations/inquire-time-dailychartprice"
TR_ID = "FHKST03010230"

# ========== Redis 연결 ==========
print("🔗 Redis 연결 시도 중...")
try:
    rds = redis.StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PW,
        decode_responses=True,
    )
    rds.ping()
    print(f"✅ Redis 연결 완료 ({REDIS_HOST}:{REDIS_PORT}, db={REDIS_DB})")
except redis.AuthenticationError:
    print("❌ Redis 인증 실패 — 비밀번호를 확인하세요.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Redis 연결 오류: {e}")
    sys.exit(1)

# ========== DB 연결 ==========
print("📡 DB 연결 시도 중...")
conn = pymysql.connect(
    host=DB_HOST,
    port=3307,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    charset="utf8mb4",
    autocommit=True,
)
cur = conn.cursor()
print("✅ DB 연결 완료")


# ========== KIS 토큰 (Redis에서 불러오기) ==========
def get_token():
    print("🔑 Redis에서 KIS Access Token 조회 중...")
    raw = rds.get("kis:admin:access-token")

    if not raw:
        raise RuntimeError("❌ Redis에 kis:admin:access-token 키가 없습니다.")

    try:
        token_data = json.loads(raw)
        if isinstance(token_data, dict) and "access_token" in token_data:
            access_token = token_data["access_token"]
        else:
            access_token = str(token_data)
    except json.JSONDecodeError:
        access_token = raw.strip()

    if not access_token:
        raise RuntimeError("❌ access_token 누락")

    ttl = rds.ttl("kis:admin:access-token")
    print(f"🔹 Redis 토큰 TTL: {ttl}s")
    print(f"✅ Access Token 확인 완료 (길이: {len(access_token)}자)")
    return access_token


# ========== 안전 GET ==========
def safe_get(url, headers, params, retries=3, sleep_sec=0.4):
    for i in range(retries):
        try:
            print(
                f"🌐 요청 중({i+1}/{retries}): {params['FID_INPUT_DATE_1']} {params['FID_INPUT_ISCD']}"
            )
            r = requests.get(url, headers=headers, params=params, timeout=10)
            if r.ok:
                return r
            else:
                print(f"⚠️ 응답 실패: {r.status_code} / {r.text[:200]}")
        except Exception as e:
            print(f"❌ 요청 오류: {e} (시도 {i+1}/{retries})")
        time.sleep(sleep_sec)
    raise RuntimeError("KIS 요청 최대 재시도 초과")


# ========== 특정 날짜 14:00 ±10분 ==========
def get_price_at_1400(stock_code: str, yyyymmdd: str) -> float | None:
    token = get_token()
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": TR_ID,
        "custtype": "P",
    }

    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": stock_code,
        "FID_INPUT_DATE_1": yyyymmdd,
        "FID_INPUT_HOUR_1": "090000",
        "FID_PW_DATA_INCU_YN": "Y",
        "FID_FAKE_TICK_INCU_YN": "",
    }

    print(f"📅 [{yyyymmdd}] 분봉 조회 시도 중...")
    r = safe_get(BASE_URL + QUOTE_PATH, headers, params)
    data = r.json()
    output = data.get("output2", []) or []
    print(f"🔹 [{yyyymmdd}] 데이터 수신: {len(output)}개")

    if not output:
        return None

    def is_near_1400(hhmmss):
        return "1350" <= hhmmss[:4] <= "1410"

    near_14 = [c for c in output if is_near_1400(c.get("stck_cntg_hour", ""))]
    if near_14:
        pick = sorted(near_14, key=lambda x: x["stck_cntg_hour"], reverse=True)[0]
    else:
        pick = output[-1]
        print(
            f"⚠️ [{yyyymmdd}] 14시 근처 없음 → 마지막 분봉 사용 ({pick['stck_cntg_hour']})"
        )

    try:
        price = float(pick["stck_prpr"])
        print(f"💰 [{yyyymmdd}] 사용 가격: {price}")
        return price
    except Exception:
        return None


# ========== 거래 생성 ==========
def generate_trades(strategy_id: int, stock_code: str, days=365):
    tz = dt.timezone(dt.timedelta(hours=9))
    today = dt.datetime.now(tz=tz).date()
    start_date = today - dt.timedelta(days=days)
    trade_count = 0
    d = start_date

    print(f"\n🚀 전략 {strategy_id} / 종목 {stock_code} 거래 생성 시작 ({days}일)")
    while d <= today:
        if d.weekday() < 5:
            yyyymmdd = d.strftime("%Y%m%d")
            price = get_price_at_1400(stock_code, yyyymmdd)
            if price:
                # ✅ 장중 랜덤 시각 (09:00~15:30)
                hour = random.randint(9, 15)
                minute = random.randint(0, 59 if hour < 15 else 30)
                executed_at = dt.datetime(
                    d.year, d.month, d.day, hour, minute, 0, tzinfo=tz
                )
                created_at = updated_at = executed_at

                trade_side = random.choice(["BUY", "SELL"])
                qty = random.randint(1, 5)
                trade_id = f"SIM_{stock_code}_{strategy_id}_{trade_count:03d}"

                print(
                    f"📝 주문 생성 중... ({trade_side}, {qty}주, {price}) [{yyyymmdd} {hour:02d}:{minute:02d}]"
                )

                # ✅ stock_order INSERT
                cur.execute(
                    """
                    INSERT INTO stock_order (
                        strategy_id,
                        trade_id,
                        order_type,
                        order_kind,
                        order_quantity,
                        order_status,
                        created_at,
                        updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        strategy_id,
                        trade_id,
                        trade_side,
                        "MARKET",
                        qty,
                        "FILLED",
                        created_at,
                        updated_at,
                    ),
                )
                order_id = cur.lastrowid

                # ✅ trade_execution INSERT (code 포함)
                cur.execute(
                    """
                    INSERT INTO trade_execution (
                        stock_order_id,
                        code,
                        trade_execution_type,
                        trade_execution_quantity,
                        trade_execution_price,
                        trade_execution_status,
                        execution_time,
                        created_at,
                        updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        order_id,
                        stock_code,
                        trade_side,
                        qty,
                        price,
                        "FILLED",
                        executed_at,
                        created_at,
                        updated_at,
                    ),
                )

                trade_count += 1
                print(f"✅ 거래 {trade_count}건 누적 완료 ({yyyymmdd})")
            else:
                print(f"⚠️ {yyyymmdd} 데이터 없음")
            time.sleep(0.25)
        d += dt.timedelta(days=1)
    print(f"🎯 총 {trade_count}건 생성 완료")


# ========== 실행 ==========
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "❗사용법: python insert_fake_trades.py <strategy_id:int> <stock_code:str>"
        )
        sys.exit(1)

    strategy_id = int(sys.argv[1])
    stock_code = sys.argv[2]

    try:
        generate_trades(strategy_id, stock_code, days=365)
    finally:
        cur.close()
        conn.close()
