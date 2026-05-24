from fastapi import APIRouter, Query
from app.config import settings
from app.database import get_db

router = APIRouter()


@router.get("/narrative")
def get_narrative(
    brand_id: str = Query(default=None),
    week: str = Query(default=None),
    narrative_type: str = Query(default="weekly_summary"),
):
    db = get_db()
    q = db.table("ai_narratives").select("*") \
        .eq("brand_id", brand_id or settings.joola_brand_id) \
        .eq("narrative_type", narrative_type)
    if week:
        q = q.eq("week_start", week)
    res = q.order("week_start", desc=True).limit(10).execute()
    return {"data": res.data or []}
