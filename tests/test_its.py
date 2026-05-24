import pytest
from app.analytics.its import run_its_analysis


def test_its_with_synthetic_event():
    values = [10.0 + i * 0.5 for i in range(20)]
    values = values[:10] + [v + 15.0 for v in values[10:]]
    result = run_its_analysis(values, event_index=10)
    assert "level_change" in result
    assert "trend_change" in result
    assert "p_value" in result
    assert result["level_change"] is not None
    assert result["level_change"] > 10


def test_its_insufficient_data():
    result = run_its_analysis([1.0, 2.0, 3.0], event_index=2)
    assert result["error"] is not None


def test_its_event_too_close_to_edge():
    values = [float(i) for i in range(15)]
    result = run_its_analysis(values, event_index=1)
    assert result["error"] is not None


def test_its_returns_r_squared():
    values = [10.0 + i * 0.3 for i in range(20)]
    values = values[:10] + [v + 20.0 for v in values[10:]]
    result = run_its_analysis(values, event_index=10)
    if result["error"] is None:
        assert 0.0 <= result["r_squared"] <= 1.0
