import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.pipelines.etl import run_etl
from app.pipelines.full_pipeline import run_full_pipeline

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def poll_new_data_job():
    """Check if new data rows arrived; if so, trigger full pipeline."""
    try:
        from app.database import get_db
        db = get_db()
        brand_id = settings.joola_brand_id

        mart_res = db.table("joola_timeseries_weekly") \
            .select("updated_at") \
            .eq("brand_id", brand_id) \
            .order("updated_at", desc=True).limit(1).execute()

        ig_res = db.table("joola_ig_weekly_snapshot") \
            .select("week_start") \
            .order("week_start", desc=True).limit(1).execute()

        mart_latest = mart_res.data[0]["updated_at"][:10] if mart_res.data else "2000-01-01"
        ig_latest = ig_res.data[0]["week_start"][:10] if ig_res.data else "2000-01-01"

        if ig_latest > mart_latest:
            logger.info(f"New data detected ({ig_latest} > {mart_latest}), triggering full pipeline")
            await run_full_pipeline("scheduler")
        else:
            logger.debug("No new data detected")
    except Exception as e:
        logger.error(f"poll_new_data_job failed: {e}")


def start_scheduler():
    scheduler.add_job(
        poll_new_data_job,
        IntervalTrigger(minutes=settings.poll_interval_minutes),
        id="poll_new_data",
        replace_existing=True,
    )
    scheduler.add_job(
        run_full_pipeline,
        IntervalTrigger(hours=1),
        id="run_full_pipeline_hourly",
        args=["scheduler"],
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Scheduler started: poll every {settings.poll_interval_minutes}min, full pipeline every 1h")


def stop_scheduler():
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")
