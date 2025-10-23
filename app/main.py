from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.domain.minute_quotes.quotes_service import start_quotes, stop_quotes
from app.domain.minute_quotes.redis_fulsher import (
    preload_from_db,
    start_scheduler,
    SYMBOLS,
    TIMEFRAMES,
)

from app.schedule.daily_quotes_scheduler import (
    start_daily_quotes_scheduler,
    shutdown_daily_quotes_scheduler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 장 시작 시 Redis Preload
    for s in SYMBOLS:
        for tf in TIMEFRAMES:
            preload_from_db(s, tf)

    # Redis → DB flush 스케줄러 시작
    start_scheduler()
    print("[Scheduler] Redis → DB Flush 스케줄러 시작됨")

    # 기존 스케줄러 + 실시간 quotes 시작
    # start_daily_quotes_scheduler()
    # await start_quotes()

    try:
        yield
    finally:
        shutdown_daily_quotes_scheduler()
        await stop_quotes()
        print("[Shutdown] All schedulers and streams stopped ✅")


app = FastAPI(title="market module", lifespan=lifespan)
