import pytest
from app.analytics.changepoint import detect_changepoints, ChangePoint


def test_detects_obvious_changepoint():
    signal = [10.0] * 10 + [50.0] * 10
    cps = detect_changepoints(signal, min_size=3)
    assert len(cps) >= 1
    assert any(8 <= cp.index <= 12 for cp in cps)


def test_no_changepoints_stable():
    signal = [10.0 + (i % 3) * 0.1 for i in range(20)]
    cps = detect_changepoints(signal, min_size=3)
    assert len(cps) == 0


def test_changepoint_pct_change():
    signal = [10.0] * 8 + [20.0] * 8
    cps = detect_changepoints(signal, min_size=3)
    assert len(cps) >= 1
    cp = cps[0]
    assert cp.pct_change > 50
    assert cp.direction == "increase"


def test_changepoint_returns_correct_structure():
    signal = [float(i) for i in range(5, 25)] + [float(i) for i in range(5, 25)]
    cps = detect_changepoints(signal)
    for cp in cps:
        assert isinstance(cp, ChangePoint)
        assert cp.pre_mean is not None
        assert cp.post_mean is not None


def test_short_signal_returns_empty():
    assert detect_changepoints([1.0, 2.0, 3.0]) == []


def test_constant_signal_returns_empty():
    assert detect_changepoints([5.0] * 20) == []
