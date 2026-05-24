from fastapi import APIRouter
from pydantic import BaseModel
from app.database import get_db

router = APIRouter()


class CausalEventCreate(BaseModel):
    event_date: str
    event_name: str
    event_type: str
    description: str | None = None
    platform: str = "all"


@router.get("/events")
def list_events():
    db = get_db()
    res = db.table("causal_events").select("*").order("event_date", desc=True).execute()
    return {"data": res.data or []}


@router.post("/events")
def create_event(body: CausalEventCreate):
    db = get_db()
    res = db.table("causal_events").insert(body.model_dump()).execute()
    return {"data": res.data[0]}
