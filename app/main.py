from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.schedule.web_socket_token_scheduler import start_scheduler, shutdown_scheduler
from app.schedule.access_token_scheduler import start_access_token_scheduler, shutdown_access_token_scheduler
from app.domain.quotes.quotes_service import start_quotes, stop_quotes

"""
스케줄링 등록 + 시세 데이터
"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    start_access_token_scheduler()

    await start_quotes()

    try:
        yield
    finally:
        shutdown_scheduler()
        shutdown_access_token_scheduler()
        await stop_quotes()


app = FastAPI(title="market module", lifespan=lifespan)
