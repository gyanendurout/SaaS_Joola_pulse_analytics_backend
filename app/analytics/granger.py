import logging
import math
import numpy as np
from scipy.stats import pearsonr

logger = logging.getLogger(__name__)

MIN_POINTS = 15  # Granger needs more data than simple correlation


def run_granger_test(
    cause: list[float],
    effect: list[float],
    max_lag: int = 4,
) -> dict:
    if len(cause) < MIN_POINTS or len(effect) < MIN_POINTS:
        return {
            "is_significant": False,
            "p_value": None,
            "f_stat": None,
            "optimal_lag": None,
            "error": f"Insufficient data: need {MIN_POINTS} points, got {min(len(cause), len(effect))}",
        }
    try:
        from statsmodels.tsa.stattools import grangercausalitytests
        import pandas as pd

        n = min(len(cause), len(effect))
        df = pd.DataFrame({"effect": effect[:n], "cause": cause[:n]})
        results = grangercausalitytests(df[["effect", "cause"]], maxlag=max_lag, verbose=False)

        best_lag = min(results.keys(), key=lambda lag: results[lag][0]["ssr_ftest"][1])
        f_stat, p_value = results[best_lag][0]["ssr_ftest"][:2]

        return {
            "is_significant": bool(p_value < 0.05),
            "p_value": float(p_value),
            "f_stat": float(f_stat),
            "optimal_lag": int(best_lag),
            "error": None,
        }
    except Exception as e:
        logger.warning(f"Granger test failed: {e}")
        return {"is_significant": False, "p_value": None, "f_stat": None, "optimal_lag": None, "error": str(e)}


def find_all_granger_pairs(
    metric_series: dict[str, list[float]],
    max_lag: int = 4,
    correlation_threshold: float = 0.3,
) -> list[dict]:
    """Pre-filter by |pearson_r| > threshold, then test Granger for each ordered pair."""
    metrics = list(metric_series.keys())
    pairs = []

    for cause in metrics:
        for effect in metrics:
            if cause == effect:
                continue
            xs = metric_series[cause]
            ys = metric_series[effect]
            n = min(len(xs), len(ys))
            if n < MIN_POINTS:
                continue
            try:
                r, _ = pearsonr(xs[:n], ys[:n])
                if math.isnan(r) or abs(r) < correlation_threshold:
                    continue
            except Exception:
                continue

            result = run_granger_test(xs[:n], ys[:n], max_lag=max_lag)
            pairs.append({"cause": cause, "effect": effect, "result": result})

    return pairs
