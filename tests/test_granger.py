import pytest
from app.analytics.granger import run_granger_test, find_all_granger_pairs


def test_granger_insufficient_data():
    result = run_granger_test([1.0, 2.0, 3.0], [4.0, 5.0, 6.0], max_lag=2)
    assert result["is_significant"] is False
    assert result["error"] is not None


def test_granger_returns_structure():
    import numpy as np
    x = [float(v) for v in np.sin(np.linspace(0, 4 * np.pi, 30))]
    y = [float(v) for v in np.sin(np.linspace(0, 4 * np.pi, 30) - np.pi / 4)]
    result = run_granger_test(x, y, max_lag=4)
    assert "is_significant" in result
    assert "p_value" in result
    assert "optimal_lag" in result


def test_find_all_pairs_filters_by_correlation():
    series = {
        "ig_views": [float(i) for i in range(20)],
        "yt_views": [float(i * 2) for i in range(20)],
        "rd_mentions": [float(i * 0.1) for i in range(20)],
    }
    pairs = find_all_granger_pairs(series, max_lag=2, correlation_threshold=0.3)
    assert isinstance(pairs, list)
    for pair in pairs:
        assert "cause" in pair
        assert "effect" in pair
        assert "result" in pair
