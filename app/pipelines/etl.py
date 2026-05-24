import logging
from datetime import datetime

from app.config import settings
from app.database import get_db
from app.pipelines.mart_builder import MartBuilder

logger = logging.getLogger(__name__)


async def run_etl(triggered_by: str = "scheduler") -> dict:
    """Fetch all platform data from Supabase and upsert into joola_timeseries_weekly."""
    db = get_db()
    brand_id = settings.joola_brand_id

    run = db.table("analytics_runs").insert({
        "run_type": "etl",
        "triggered_by": triggered_by,
        "status": "running",
    }).execute()
    run_id = run.data[0]["id"]

    try:
        ig_res = db.table("joola_ig_weekly_snapshot") \
            .select("week_start,posts_published,total_views,avg_engagement_rate,purchase_intent_count,complaint_count") \
            .execute()

        yt_res = db.table("yt_channel_weekly") \
            .select("year,week_number,total_views,videos_uploaded_this_week") \
            .eq("brand_id", brand_id).execute()

        tt_res = db.table("tiktok_videos") \
            .select("posted_at,view_count") \
            .eq("brand_id", brand_id) \
            .not_.is_("posted_at", "null").execute()

        rd_res = db.table("reddit_mentions") \
            .select("posted_at,upvotes,is_opportunity") \
            .eq("brand_id", brand_id) \
            .not_.is_("posted_at", "null").execute()

        rows = MartBuilder.build_all_rows(
            brand_id,
            ig_res.data or [],
            yt_res.data or [],
            tt_res.data or [],
            rd_res.data or [],
        )

        if rows:
            upsert_data = [r.to_dict() for r in rows]
            db.table("joola_timeseries_weekly").upsert(
                upsert_data,
                on_conflict="brand_id,week_start,platform,metric_name"
            ).execute()

        db.table("analytics_runs").update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "rows_processed": len(rows),
        }).eq("id", run_id).execute()

        logger.info(f"ETL completed: {len(rows)} rows upserted")
        return {"run_id": run_id, "rows_processed": len(rows), "status": "completed"}

    except Exception as e:
        db.table("analytics_runs").update({
            "status": "failed",
            "completed_at": datetime.utcnow().isoformat(),
            "error_message": str(e),
        }).eq("id", run_id).execute()
        logger.error(f"ETL failed: {e}")
        raise
