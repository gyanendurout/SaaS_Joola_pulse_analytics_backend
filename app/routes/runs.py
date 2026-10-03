import asyncio
from fastapi import APIRouter, BackgroundTasks, Query
from app.config import ON_VERCEL
from app.database import get_db
from app.pipelines.full_pipeline import run_full_pipeline

router = APIRouter()


@router.get("/runs")
def get_runs(limit: int = Query(default=20, ge=1, le=100)):
    db = get_db()
    res = db.table("analytics_runs").select("*").order("started_at", desc=True).limit(limit).execute()
    return {"data": res.data or []}


@router.post("/runs/trigger")
async def trigger_pipeline(background_tasks: BackgroundTasks):
    if ON_VERCEL:
        # Vercel can freeze the instance once the response is sent, killing a
        # BackgroundTask - run inline (bounded by the function's maxDuration).
        result = await _run_pipeline_task()
        return {"status": "completed", "result": result}
    background_tasks.add_task(_run_pipeline_task)
    return {"status": "triggered", "message": "Pipeline started in background"}


async def _run_pipeline_task() -> None:
    result = await run_full_pipeline(triggered_by="manual")
    return result
