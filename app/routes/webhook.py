import logging
from fastapi import APIRouter, BackgroundTasks

from app.config import ON_VERCEL
from app.pipelines.full_pipeline import run_full_pipeline

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/webhook/scraper")
async def scraper_webhook(payload: dict, background_tasks: BackgroundTasks):
    """Called by the existing scraper backend when new data is available."""
    logger.info(f"Webhook received: {payload}")
    if ON_VERCEL:
        # See routes/runs.py - deferred tasks are not reliable on Vercel.
        result = await run_full_pipeline("webhook")
        return {"status": "completed", "result": result}
    background_tasks.add_task(run_full_pipeline, "webhook")
    return {"status": "queued", "message": "Analytics pipeline triggered"}
