from fastapi import APIRouter, Query
from app.config import settings
from app.database import get_db

router = APIRouter()


@router.get("/forecast")
def get_forecast(
    brand_id: str = Query(default=None),
    metric: str = Query(default="ig_views"),
    horizon: int = Query(default=8),
):
    db = get_db()
    res = db.table("forecast_results").select("*") \
        .eq("brand_id", brand_id or settings.joola_brand_id) \
        .eq("metric", metric) \
        .order("forecast_week").execute()
    return {"data": res.data or [], "meta": {"metric": metric, "horizon_weeks": horizon}}
