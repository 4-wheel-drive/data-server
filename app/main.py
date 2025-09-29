from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.schedule.web_socket_token_scheduler import start_scheduler, shutdown_scheduler
from app.schedule.access_token_scheduler import start_access_token_scheduler, shutdown_access_token_scheduler
from app.domain.quotes.quotes_service import start_quotes, stop_quotes
from app.domain.quotes.quotes_service import subscribe
from app.schedule.access_token_scheduler import get_access_token, start_access_token_scheduler, shutdown_access_token_scheduler
from app.schedule.daily_quotes_scheduler import start_daily_quotes_scheduler, shutdown_daily_quotes_scheduler

"""
스케줄링 등록 + 시세 데이터
"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    start_access_token_scheduler()
    start_daily_quotes_scheduler()
    
    await start_quotes()

    try:
        yield
    finally:
        shutdown_scheduler()
        shutdown_access_token_scheduler()
        shutdown_daily_quotes_scheduler()

        await stop_quotes()

app = FastAPI(title="market module", lifespan=lifespan)