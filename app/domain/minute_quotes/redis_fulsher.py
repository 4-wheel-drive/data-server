import json
import pymysql
from datetime import datetime
from decimal import Decimal
from apscheduler.schedulers.background import BackgroundScheduler
from app.infra.redis_client import redis_client

# ==============================
# DB 설정
# ==============================
DB_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "admin",
    "password": "admin1024",
    "db": "modular1",
    "charset": "utf8mb4",
}

# ==============================
# 대상 심볼 / 타임프레임
# ==============================
SYMBOLS = [
    "005930",
    "000660",
    "035420",
    "005380",
    "051910",
    "006400",
    "035720",
    "000270",
    "068270",
    "207940",
    "005490",
    "066570",
    "012330",
    "000810",
    "015760",
    "259960",
    "086520",
    "247540",
    "034730",
    "018260",
]
TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h"]


def get_last_db_time(cursor, symbol, timeframe):
    cursor.execute(
        "SELECT MAX(t) FROM candle WHERE symbol=%s AND timeframe=%s",
        (symbol, timeframe),
    )
    result = cursor.fetchone()[0]
    return result


def insert_candles(symbol, timeframe, candles):
    """MariaDB Bulk Insert (시간 포맷 자동 보정)"""
    if not candles:
        return

    with pymysql.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            values = []
            for c in candles:
                try:
                    try:
                        t = datetime.fromisoformat(c["t"])
                    except ValueError:
                        t = datetime.strptime(c["t"], "%Y%m%d%H%M")
                except Exception as e:
                    print(f"[WARN] 시간 파싱 실패 ({c.get('t')}): {e}")
                    continue

                values.append(
                    (
                        t,
                        symbol,
                        timeframe,
                        c["o"],
                        c["h"],
                        c["l"],
                        c["c"],
                        c["v"],
                        c.get("tick_strength"),
                        c.get("cumulative_volume"),
                        c.get("cumulative_value"),
                        c.get("change_rate"),
                    )
                )

            if not values:
                return

            sql = """
            INSERT INTO candle (
                t, symbol, timeframe, open, high, low, close, volume,
                tick_strength, cumulative_volume, cumulative_value, change_rate
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                close=VALUES(close),
                high=GREATEST(high, VALUES(high)),
                low=LEAST(low, VALUES(low)),
                volume=VALUES(volume)
            """

            cursor.executemany(sql, values)
            conn.commit()
            print(f"[DB] {symbol}-{timeframe}: {cursor.rowcount} rows bulk inserted ✅")


# ==============================
# Redis → DB Flush
# ==============================
def flush_redis_to_db():
    print(f"\n[Scheduler] flush_redis_to_db 실행 ({datetime.now().isoformat()})")

    for symbol in SYMBOLS:
        for tf in TIMEFRAMES:
            key = f"C:{symbol}:{tf}"
            offset_key = f"{key}:last_flushed"

            try:
                candles_raw = redis_client.lrange(key, 0, -1)
                if not candles_raw:
                    continue

                # Redis LPUSH 순서 보정 (최신→오래된 → 역순)
                candles = [json.loads(c) for c in reversed(candles_raw)]

                # Redis offset 읽기
                offset_str = redis_client.get(offset_key)

                offset_time = (
                    datetime.fromisoformat(offset_str.decode()) if offset_str else None
                )

                # offset 이후 봉만 필터링
                if offset_time:
                    new_candles = [
                        c
                        for c in candles
                        if datetime.fromisoformat(c["t"]) > offset_time
                    ]
                else:
                    # offset 없으면 DB MAX(t) fallback
                    with pymysql.connect(**DB_CONFIG) as conn:
                        with conn.cursor() as cursor:
                            db_last = get_last_db_time(cursor, symbol, tf)
                    new_candles = [
                        c
                        for c in candles
                        if not db_last or datetime.fromisoformat(c["t"]) > db_last
                    ]

                if not new_candles:
                    continue

                # DB에 bulk insert
                insert_candles(symbol, tf, new_candles)

                # offset 갱신 (가장 최신 봉 기준)
                latest_time = max(datetime.fromisoformat(c["t"]) for c in new_candles)
                redis_client.set(offset_key, latest_time.isoformat())
                print(f"[Offset 갱신] {offset_key} → {latest_time}")

            except Exception as e:
                print(f"[ERROR] {symbol}-{tf} flush 실패: {e}")
                continue

    print("[Scheduler] Redis → DB Flush 완료")


# ==============================
# 장 시작 시 Redis Warm-up (DB → Redis)
# ==============================
def preload_from_db(symbol, timeframe, limit=200):
    """DB에서 최근 N개 봉을 Redis로 복구"""
    with pymysql.connect(**DB_CONFIG) as conn:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                """
                SELECT t, open AS o, high AS h, low AS l, close AS c, volume AS v,
                       tick_strength, cumulative_volume, cumulative_value, change_rate
                FROM candle
                WHERE symbol=%s AND timeframe=%s
                ORDER BY t DESC
                LIMIT %s
                """,
                (symbol, timeframe, limit),
            )
            rows = cursor.fetchall()

    if not rows:
        print(f"[Preload] No data found for {symbol}:{timeframe}")
        return

    key = f"C:{symbol}:{timeframe}"
    pipe = redis_client.pipeline()
    for row in rows:
        # ✅ datetime → str
        if isinstance(row["t"], datetime):
            row["t"] = row["t"].isoformat()
        # ✅ Decimal → float
        for k, v in row.items():
            if isinstance(v, Decimal):
                row[k] = float(v)
        pipe.lpush(key, json.dumps(row))
    pipe.ltrim(key, 0, limit - 1)
    pipe.execute()
    print(f"[Preload] {symbol}:{timeframe} {len(rows)} candles loaded to Redis ✅")


# ==============================
# Scheduler Start
# ==============================
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(flush_redis_to_db, "interval", minutes=30)
    scheduler.start()
    print("[Scheduler] Redis → DB Flush 스케줄러 시작됨 (30분 간격)")


# ==============================
# Main
# ==============================
if __name__ == "__main__":
    # 장 시작 시 DB → Redis preload
    for s in SYMBOLS:
        for tf in TIMEFRAMES:
            preload_from_db(s, tf)
    print("[Init] Redis Warm-up 완료 (모든 심볼 + 모든 타임프레임 로드)")

    # flush 스케줄러 실행
    start_scheduler()

    import time

    while True:
        time.sleep(60)
