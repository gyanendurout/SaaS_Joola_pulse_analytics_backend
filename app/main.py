from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.scheduler.jobs import start_scheduler, stop_scheduler
from app.routes import (
    timeseries, correlation, granger, changepoints,
    its, composite, forecast, narrative, events, runs, webhook,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.enable_scheduler:
        start_scheduler()
    yield
    if settings.enable_scheduler:
        stop_scheduler()


app = FastAPI(title="JOOLA Analytics", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "https://*.railway.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(timeseries.router, prefix="/api")
app.include_router(correlation.router, prefix="/api")
app.include_router(granger.router, prefix="/api")
app.include_router(changepoints.router, prefix="/api")
app.include_router(its.router, prefix="/api")
app.include_router(composite.router, prefix="/api")
app.include_router(forecast.router, prefix="/api")
app.include_router(narrative.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(runs.router, prefix="/api")
app.include_router(webhook.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "joola-analytics"}
