"""Vercel Cron entry point — replaces the in-process APScheduler on Vercel."""
import hmac
import logging

from fastapi import APIRouter, Header, HTTPException

from app.config import settings
from app.pipelines.full_pipeline import run_full_pipeline

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/cron/pipeline")
async def cron_pipeline(authorization: str | None = Header(default=None)) -> dict:
    """Run the full pipeline synchronously, within the function's maxDuration.

    Runs inline rather than as a BackgroundTask: Vercel may freeze the instance
    as soon as the response is sent, which would kill a deferred task.
    """
    if not settings.cron_secret:
        raise HTTPException(status_code=503, detail="CRON_SECRET is not configured")
    expected = f"Bearer {settings.cron_secret}"
    if not hmac.compare_digest(authorization or "", expected):
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info("Cron: running full pipeline")
    return await run_full_pipeline(triggered_by="cron")
