from fastapi import APIRouter, Query
from app.config import settings
from app.database import get_db
from datetime import datetime, timezone

router = APIRouter()


@router.get("/timeseries")
def get_timeseries(
    brand_id: str = Query(default=None),
    platform: str = Query(default="all"),
    weeks: int = Query(default=26, ge=4, le=104),
):
    db = get_db()
    bid = brand_id or settings.joola_brand_id
    q = db.table("joola_timeseries_weekly") \
        .select("week_start,platform,metric_name,value") \
        .eq("brand_id", bid) \
        .order("week_start")
    if platform != "all":
        q = q.eq("platform", platform)
    res = q.execute()
    data = res.data or []
    weeks_set = sorted({r["week_start"] for r in data})[-weeks:]
    filtered = [r for r in data if r["week_start"] in weeks_set]
    return {"data": filtered, "meta": {"weeks": len(weeks_set), "generated_at": datetime.now(timezone.utc).isoformat()}}
