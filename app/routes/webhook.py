import logging
from fastapi import APIRouter, BackgroundTasks

from app.pipelines.full_pipeline import run_full_pipeline

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/webhook/scraper")
async def scraper_webhook(payload: dict, background_tasks: BackgroundTasks):
    """Called by the existing scraper backend when new data is available."""
    logger.info(f"Webhook received: {payload}")
    background_tasks.add_task(run_full_pipeline, "webhook")
    return {"status": "queued", "message": "Analytics pipeline triggered"}
