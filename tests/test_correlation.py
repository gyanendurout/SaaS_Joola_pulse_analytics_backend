import pytest
from app.analytics.correlation import compute_pearson, compute_spearman, build_correlation_matrix


def test_pearson_perfect_positive():
    xs = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ys = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0]
    r, p = compute_pearson(xs, ys)
    assert abs(r - 1.0) < 0.0001
    assert p < 0.001


def test_pearson_insufficient_data():
    assert compute_pearson([1.0, 2.0], [3.0, 4.0]) == (None, None)


def test_spearman_monotone():
    xs = [1.0, 4.0, 2.0, 8.0, 5.0, 7.0]
    ys = [10.0, 40.0, 20.0, 80.0, 50.0, 70.0]
    r, p = compute_spearman(xs, ys)
    assert abs(r - 1.0) < 0.0001


def test_correlation_matrix_shape():
    data = {
        "ig_views": [100.0, 200.0, 150.0, 300.0, 250.0, 180.0],
        "yt_views": [1000.0, 2000.0, 1500.0, 3000.0, 2500.0, 1800.0],
        "rd_mentions": [5.0, 10.0, 7.0, 15.0, 12.0, 9.0],
    }
    matrix = build_correlation_matrix(data, min_points=4)
    assert "ig_views" in matrix
    assert "yt_views" in matrix["ig_views"]
    assert matrix["ig_views"]["yt_views"]["pearson_r"] is not None


def test_pearson_negative_correlation():
    xs = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ys = [12.0, 10.0, 8.0, 6.0, 4.0, 2.0]
    r, p = compute_pearson(xs, ys)
    assert r is not None
    assert r < -0.99
