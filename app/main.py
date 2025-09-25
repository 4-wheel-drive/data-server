from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.schedule.token_scheduler import start_scheduler, shutdown_scheduler, approval_key

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    start_scheduler()
    try:
        yield
    finally:
        shutdown_scheduler()

app = FastAPI(title="HanT0o Trading API", lifespan=lifespan)

@app.get("/approval")
def read_approval_key():
    return {"approval_key": approval_key}
