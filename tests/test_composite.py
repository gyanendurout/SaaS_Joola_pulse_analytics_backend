import pytest
from app.analytics.composite import compute_composite_scores, normalize_series, ScoreRow


def test_normalize_all_equal():
    result = normalize_series([5.0, 5.0, 5.0, 5.0])
    assert all(v == 0.0 for v in result)


def test_normalize_range():
    result = normalize_series([0.0, 5.0, 10.0])
    assert abs(result[0] - 0.0) < 0.001
    assert abs(result[1] - 0.5) < 0.001
    assert abs(result[2] - 1.0) < 0.001


def test_attention_score_in_range():
    weeks = ["2026-04-28", "2026-05-05", "2026-05-12"]
    data = {
        "ig_views": [10000.0, 15000.0, 12000.0],
        "yt_views": [5000.0, 7000.0, 6000.0],
        "tt_views": [100000.0, 80000.0, 120000.0],
        "rd_mentions": [10.0, 15.0, 8.0],
        "rd_upvotes": [50.0, 80.0, 30.0],
    }
    scores = compute_composite_scores(weeks, data)
    for score in scores:
        assert 0.0 <= score.attention_score <= 100.0
        assert isinstance(score, ScoreRow)


def test_sales_score_in_range():
    weeks = ["2026-04-28", "2026-05-05", "2026-05-12"]
    data = {
        "ig_purchase_intent": [5.0, 10.0, 8.0],
        "rd_opportunity": [2.0, 5.0, 3.0],
        "ig_engagement_rate": [3.5, 4.2, 3.8],
    }
    scores = compute_composite_scores(weeks, data)
    for score in scores:
        assert 0.0 <= score.sales_likelihood_score <= 100.0


def test_score_count_matches_weeks():
    weeks = ["2026-04-28", "2026-05-05", "2026-05-12", "2026-05-19"]
    data = {"ig_views": [1.0, 2.0, 3.0, 4.0]}
    scores = compute_composite_scores(weeks, data)
    assert len(scores) == 4
