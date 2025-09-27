from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.schedule.web_socket_token_scheduler import start_scheduler, shutdown_scheduler
from app.domain.qutoes.qutoes_service import subscribe
from app.schedule.access_token_scheduler import get_access_token, start_access_token_scheduler, shutdown_access_token_scheduler

"""
스케줄링 등록
"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    start_access_token_scheduler()
    try:
        yield
    finally:
        shutdown_scheduler()
        shutdown_access_token_scheduler()


app = FastAPI(title="market module", lifespan=lifespan)
