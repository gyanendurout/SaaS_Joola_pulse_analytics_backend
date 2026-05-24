import logging
from openai import AsyncOpenAI

from app.config import settings
from app.database import get_db
from app.pipelines.etl import run_etl
from app.analytics.correlation import build_correlation_matrix
from app.analytics.granger import find_all_granger_pairs
from app.analytics.changepoint import detect_changepoints
from app.analytics.composite import compute_composite_scores
from app.agents.correlation import CorrelationInterpreterAgent
from app.agents.granger import GrangerInterpreterAgent
from app.agents.changepoint import ChangepointLabelAgent
from app.agents.composite import CompositeScoreAgent
from app.agents.narrative import WeeklyNarrativeAgent

logger = logging.getLogger(__name__)

METRIC_NAMES = [
    "ig_views", "ig_posts", "ig_engagement_rate", "ig_purchase_intent", "ig_complaints",
    "yt_views", "yt_videos_uploaded",
    "tt_videos", "tt_views",
    "rd_mentions", "rd_upvotes", "rd_opportunity",
]


def _get_openai_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.openai_api_key)


async def _fetch_timeseries(db, brand_id: str, weeks: int = 26) -> tuple[list[str], dict[str, list[float]]]:
    res = db.table("joola_timeseries_weekly") \
        .select("week_start,metric_name,value") \
        .eq("brand_id", brand_id) \
        .order("week_start").execute()

    week_set = sorted({r["week_start"] for r in (res.data or [])})[-weeks:]
    series: dict[str, list[float]] = {m: [] for m in METRIC_NAMES}

    for week in week_set:
        week_data = {r["metric_name"]: r["value"] for r in res.data if r["week_start"] == week}
        for metric in METRIC_NAMES:
            series[metric].append(week_data.get(metric, 0.0))

    return week_set, series


async def run_full_pipeline(triggered_by: str = "scheduler") -> dict:
    logger.info(f"Starting full analytics pipeline (triggered_by={triggered_by})")
    db = get_db()
    brand_id = settings.joola_brand_id
    client = _get_openai_client()

    # Step 1: ETL
    etl_result = await run_etl(triggered_by)
    weeks, series = await _fetch_timeseries(db, brand_id)

    if len(weeks) < 6:
        logger.warning("Not enough data weeks for analytics (need ≥6)")
        return {"status": "skipped", "reason": "insufficient_data", "weeks": len(weeks)}

    run_id = etl_result.get("run_id")

    # Step 2: Correlation
    matrix = build_correlation_matrix(series)
    top_pairs = sorted(
        [{"metric_a": a, "metric_b": b, "pearson_r": matrix[a][b]["pearson_r"]}
         for a in matrix for b in matrix[a] if a < b and matrix[a][b]["pearson_r"] is not None],
        key=lambda x: abs(x["pearson_r"]), reverse=True
    )[:10]
    corr_agent = CorrelationInterpreterAgent(client, settings.openai_model_fast)
    corr_narrative = await corr_agent.interpret({"top_pairs": top_pairs}) if top_pairs else ""

    corr_rows = []
    for a in matrix:
        for b in matrix[a]:
            if a >= b:
                continue
            cell = matrix[a][b]
            if cell["pearson_r"] is None:
                continue
            is_top = top_pairs and (a, b) == (top_pairs[0]["metric_a"], top_pairs[0]["metric_b"])
            corr_rows.append({
                "run_id": run_id, "brand_id": brand_id,
                "metric_a": a, "metric_b": b,
                "pearson_r": cell["pearson_r"],
                "spearman_r": cell["spearman_r"],
                "p_value": cell["p_value"],
                "n_weeks": cell["n_weeks"],
                "window_weeks": len(weeks),
                "ai_narrative": corr_narrative if is_top else None,
            })
    if corr_rows:
        db.table("correlation_results").insert(corr_rows).execute()

    # Step 3: Granger
    granger_pairs = find_all_granger_pairs(series)
    granger_agent = GrangerInterpreterAgent(client, settings.openai_model_fast)
    granger_rows = []
    for pair in granger_pairs:
        narrative = None
        if pair["result"]["is_significant"]:
            narrative = await granger_agent.interpret({
                "cause_metric": pair["cause"],
                "effect_metric": pair["effect"],
                "optimal_lag": pair["result"]["optimal_lag"],
                "p_value": pair["result"]["p_value"],
            })
        granger_rows.append({
            "run_id": run_id, "brand_id": brand_id,
            "cause_metric": pair["cause"], "effect_metric": pair["effect"],
            "max_lag_weeks": 4,
            "optimal_lag": pair["result"]["optimal_lag"],
            "f_stat": pair["result"]["f_stat"],
            "p_value": pair["result"]["p_value"],
            "is_significant": pair["result"]["is_significant"],
            "ai_narrative": narrative,
        })
    if granger_rows:
        db.table("granger_results").insert(granger_rows).execute()

    # Step 4: Changepoints
    cp_agent = ChangepointLabelAgent(client, settings.openai_model_fast)
    cp_rows = []
    for metric, values in series.items():
        cps = detect_changepoints(values)
        for cp in cps:
            week = weeks[min(cp.index, len(weeks) - 1)]
            label = await cp_agent.label_changepoint({
                "metric": metric, "changepoint_week": week,
                "pct_change": cp.pct_change, "direction": cp.direction,
                "pre_mean": cp.pre_mean, "post_mean": cp.post_mean,
            })
            cp_rows.append({
                "run_id": run_id, "brand_id": brand_id,
                "metric": metric, "changepoint_week": week,
                "pre_mean": cp.pre_mean, "post_mean": cp.post_mean,
                "pct_change": cp.pct_change, "direction": cp.direction,
                "ai_label": label,
            })
    if cp_rows:
        db.table("changepoint_results").insert(cp_rows).execute()

    # Step 5: Composite scores
    score_rows_data = compute_composite_scores(weeks, series)
    score_agent = CompositeScoreAgent(client, settings.openai_model_fast)
    all_score_upserts = [
        {
            "brand_id": brand_id, "week_start": row.week_start,
            "attention_score": row.attention_score,
            "sales_likelihood_score": row.sales_likelihood_score,
            "attention_components": row.attention_components,
            "sales_components": row.sales_components,
        }
        for row in score_rows_data
    ]
    for row in score_rows_data[-4:]:
        narrative = await score_agent.interpret({
            "week_start": row.week_start,
            "attention_score": row.attention_score,
            "sales_likelihood_score": row.sales_likelihood_score,
            "attention_components": row.attention_components,
            "sales_components": row.sales_components,
        })
        for upsert in all_score_upserts:
            if upsert["week_start"] == row.week_start:
                upsert["ai_narrative"] = narrative
    if all_score_upserts:
        db.table("composite_scores_weekly").upsert(
            all_score_upserts, on_conflict="brand_id,week_start"
        ).execute()

    # Step 6: Weekly narrative
    if weeks:
        latest_week = weeks[-1]
        narrative_agent = WeeklyNarrativeAgent(client, settings.openai_model_smart)
        summary = await narrative_agent.generate_summary({
            "week_start": latest_week,
            "top_correlations": top_pairs[:3],
            "significant_granger": [p for p in granger_pairs if p["result"]["is_significant"]][:3],
            "changepoints_this_week": [r for r in cp_rows if r["changepoint_week"] == latest_week],
            "attention_score": score_rows_data[-1].attention_score if score_rows_data else 0,
            "sales_likelihood": score_rows_data[-1].sales_likelihood_score if score_rows_data else 0,
        })
        db.table("ai_narratives").upsert({
            "brand_id": brand_id,
            "week_start": latest_week,
            "narrative_type": "weekly_summary",
            "title": summary.get("title", "Weekly Insights"),
            "body": summary.get("body", ""),
            "key_points": summary.get("key_points", []),
            "model_used": settings.openai_model_smart,
        }, on_conflict="brand_id,week_start,narrative_type").execute()

    logger.info("Full analytics pipeline completed")
    return {
        "status": "completed",
        "weeks_processed": len(weeks),
        "correlations": len(corr_rows),
        "granger_pairs": len(granger_rows),
        "changepoints": len(cp_rows),
        "composite_scores": len(score_rows_data),
    }
