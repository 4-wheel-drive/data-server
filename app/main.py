from fastapi import FastAPI
from contextlib import asynccontextmanager

# from app.schedule.web_socket_token_scheduler import start_scheduler, shutdown_scheduler
# from app.schedule.access_token_scheduler import start_access_token_scheduler, shutdown_access_token_scheduler
from app.domain.minute_quotes.quotes_service import start_quotes, stop_quotes

# from app.schedule.daily_quotes_scheduler import (
#     start_daily_quotes_scheduler,
#     shutdown_daily_quotes_scheduler,
# )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start_scheduler()
    # start_access_token_scheduler()
    # start_daily_quotes_scheduler()

    await start_quotes()

    try:
        yield
    finally:
        # shutdown_scheduler()
        # shutdown_access_token_scheduler()
        # shutdown_daily_quotes_scheduler()
        await stop_quotes()


app = FastAPI(title="market module", lifespan=lifespan)
# app = FastAPI(title="market module")
