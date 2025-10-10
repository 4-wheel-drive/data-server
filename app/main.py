from fastapi import FastAPI
from contextlib import asynccontextmanager
from schedule.web_socket_token_scheduler import start_scheduler, shutdown_scheduler
from schedule.access_token_scheduler import start_access_token_scheduler, shutdown_access_token_scheduler
from domain.minute_quotes.quotes_service import start_quotes, stop_quotes
from schedule.daily_quotes_scheduler import start_daily_quotes_scheduler, shutdown_daily_quotes_scheduler
from domain.minute_quotes.mock_ws_client import mock_subscribe


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

"""  
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mock_task = asyncio.create_task(
        mock_subscribe("005930", "dummy-key", on_candle, interval=0.05)
    )
    try:
        yield
    finally:
        app.state.mock_task.cancel()
        try:
            await app.state.mock_task
        except asyncio.CancelledError:
            pass
"""

app = FastAPI(title="market module", lifespan=lifespan)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI server with schedulers...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

