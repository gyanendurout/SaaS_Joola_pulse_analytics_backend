from fastapi import APIRouter, Query
from app.config import settings
from app.database import get_db

router = APIRouter()


@router.get("/changepoints")
def get_changepoints(brand_id: str = Query(default=None), metric: str = Query(default=None)):
    db = get_db()
    q = db.table("changepoint_results").select("*").eq("brand_id", brand_id or settings.joola_brand_id)
    if metric:
        q = q.eq("metric", metric)
    res = q.order("changepoint_week", desc=True).execute()
    return {"data": res.data or []}
