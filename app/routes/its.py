from fastapi import APIRouter, Query
from app.config import settings
from app.database import get_db

router = APIRouter()


@router.get("/its")
def get_its(brand_id: str = Query(default=None)):
    db = get_db()
    res = db.table("its_results").select("*") \
        .eq("brand_id", brand_id or settings.joola_brand_id) \
        .order("created_at", desc=True).execute()
    return {"data": res.data or []}
