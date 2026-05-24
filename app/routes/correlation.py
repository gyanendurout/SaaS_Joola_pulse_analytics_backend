from fastapi import APIRouter, Query
from app.config import settings
from app.database import get_db

router = APIRouter()


@router.get("/correlation")
def get_correlation(brand_id: str = Query(default=None), weeks: int = Query(default=13)):
    db = get_db()
    res = db.table("correlation_results").select("*") \
        .eq("brand_id", brand_id or settings.joola_brand_id) \
        .order("created_at", desc=True).limit(200).execute()
    return {"data": res.data or [], "meta": {"window_weeks": weeks}}
