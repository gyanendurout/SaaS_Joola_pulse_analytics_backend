import pytest
from unittest.mock import MagicMock
from app.pipelines.mart_builder import MartBuilder, MartRow, week_monday


def test_ig_snapshot_to_rows():
    ig_data = [
        {
            "week_start": "2026-05-12",
            "total_views": 10000,
            "posts_published": 5,
            "avg_engagement_rate": 0.045,
            "purchase_intent_count": 12,
            "complaint_count": 2,
        }
    ]
    rows = MartBuilder._ig_to_rows("04db8591-37a3-4634-9d11-536975fa6935", ig_data)
    assert len(rows) == 5
    metrics = {r.metric_name: r.value for r in rows}
    assert metrics["ig_views"] == 10000
    assert metrics["ig_posts"] == 5
    assert abs(metrics["ig_engagement_rate"] - 4.5) < 0.01
    assert metrics["ig_purchase_intent"] == 12
    assert metrics["ig_complaints"] == 2


def test_week_monday_conversion():
    assert week_monday("2026-05-13") == "2026-05-11"  # Wednesday → Monday
    assert week_monday("2026-05-11") == "2026-05-11"  # Monday stays Monday
    assert week_monday("2026-05-17") == "2026-05-11"  # Sunday → Monday of that week


def test_tiktok_grouping():
    videos = [
        {"posted_at": "2026-05-12T10:00:00Z", "view_count": 5000},
        {"posted_at": "2026-05-14T12:00:00Z", "view_count": 8000},
        {"posted_at": "2026-05-19T09:00:00Z", "view_count": 3000},
    ]
    rows = MartBuilder._tiktok_to_rows("04db8591-37a3-4634-9d11-536975fa6935", videos)
    week_rows = {(r.week_start, r.metric_name): r.value for r in rows}
    assert week_rows[("2026-05-11", "tt_videos")] == 2
    assert week_rows[("2026-05-11", "tt_views")] == 13000
    assert week_rows[("2026-05-18", "tt_videos")] == 1


def test_reddit_grouping():
    mentions = [
        {"posted_at": "2026-05-12T10:00:00Z", "upvotes": 50, "is_opportunity": True},
        {"posted_at": "2026-05-13T12:00:00Z", "upvotes": 30, "is_opportunity": False},
        {"posted_at": "2026-05-19T09:00:00Z", "upvotes": 20, "is_opportunity": True},
    ]
    rows = MartBuilder._reddit_to_rows("test-brand", mentions)
    week_rows = {(r.week_start, r.metric_name): r.value for r in rows}
    assert week_rows[("2026-05-11", "rd_mentions")] == 2
    assert week_rows[("2026-05-11", "rd_upvotes")] == 80
    assert week_rows[("2026-05-11", "rd_opportunity")] == 1
