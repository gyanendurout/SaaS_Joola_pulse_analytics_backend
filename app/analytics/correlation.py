import math
from scipy.stats import pearsonr, spearmanr
import numpy as np


MIN_POINTS = 6


def _safe_float(v: float) -> float | None:
    try:
        f = float(v)
        return None if math.isnan(f) or math.isinf(f) else f
    except (TypeError, ValueError):
        return None


def compute_pearson(xs: list[float], ys: list[float]) -> tuple[float | None, float | None]:
    if len(xs) < MIN_POINTS or len(ys) < MIN_POINTS:
        return None, None
    try:
        r, p = pearsonr(xs, ys)
        return _safe_float(r), _safe_float(p)
    except Exception:
        return None, None


def compute_spearman(xs: list[float], ys: list[float]) -> tuple[float | None, float | None]:
    if len(xs) < MIN_POINTS or len(ys) < MIN_POINTS:
        return None, None
    try:
        r, p = spearmanr(xs, ys)
        return _safe_float(r), _safe_float(p)
    except Exception:
        return None, None


def build_correlation_matrix(
    metric_series: dict[str, list[float]],
    min_points: int = MIN_POINTS,
) -> dict[str, dict[str, dict]]:
    """
    Given {metric_name: [ordered weekly values]}, returns a nested dict:
    matrix[metric_a][metric_b] = {pearson_r, spearman_r, p_value, n_weeks}
    """
    metrics = list(metric_series.keys())
    matrix: dict[str, dict] = {m: {} for m in metrics}

    for m_a in metrics:
        for m_b in metrics:
            xs = metric_series[m_a]
            ys = metric_series[m_b]
            n = min(len(xs), len(ys))
            xs, ys = xs[:n], ys[:n]
            pearson_r, p_val = compute_pearson(xs, ys)
            spearman_r, _ = compute_spearman(xs, ys)
            matrix[m_a][m_b] = {
                "pearson_r": pearson_r,
                "spearman_r": spearman_r,
                "p_value": p_val,
                "n_weeks": n,
            }

    return matrix
