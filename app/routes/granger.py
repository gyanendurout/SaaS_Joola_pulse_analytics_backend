from fastapi import APIRouter, Query
from app.config import settings
from app.database import get_db

router = APIRouter()


@router.get("/granger")
def get_granger(brand_id: str = Query(default=None)):
    db = get_db()
    res = db.table("granger_results").select("*") \
        .eq("brand_id", brand_id or settings.joola_brand_id) \
        .order("created_at", desc=True).limit(100).execute()
    return {"data": res.data or []}
