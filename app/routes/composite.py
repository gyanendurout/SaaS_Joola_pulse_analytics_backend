from fastapi import APIRouter, Query
from app.config import settings
from app.database import get_db

router = APIRouter()


@router.get("/composite-scores")
def get_composite_scores(brand_id: str = Query(default=None), weeks: int = Query(default=26)):
    db = get_db()
    res = db.table("composite_scores_weekly").select("*") \
        .eq("brand_id", brand_id or settings.joola_brand_id) \
        .order("week_start", desc=True).limit(weeks).execute()
    return {"data": sorted(res.data or [], key=lambda r: r["week_start"])}
