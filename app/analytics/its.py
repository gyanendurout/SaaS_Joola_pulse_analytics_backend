import numpy as np
import logging

logger = logging.getLogger(__name__)
MIN_POINTS = 10


def run_its_analysis(values: list[float], event_index: int) -> dict:
    """
    Interrupted Time Series using OLS.
    Returns level_change, trend_change, p_value, r_squared.
    """
    n = len(values)
    if n < MIN_POINTS or event_index < 3 or event_index >= n - 3:
        return {
            "level_change": None,
            "trend_change": None,
            "p_value": None,
            "r_squared": None,
            "error": f"Insufficient data (n={n}, event_index={event_index})",
        }
    try:
        import statsmodels.api as sm
        time = np.arange(n, dtype=float)
        event_dummy = np.array([0.0] * event_index + [1.0] * (n - event_index))
        time_after = np.array([0.0] * event_index + [float(i - event_index) for i in range(event_index, n)])
        X = sm.add_constant(np.column_stack([time, event_dummy, time_after]))
        y = np.array(values)
        model = sm.OLS(y, X).fit()
        return {
            "level_change": float(model.params[2]),
            "trend_change": float(model.params[3]),
            "p_value": float(model.pvalues[2]),
            "r_squared": float(model.rsquared),
            "error": None,
        }
    except Exception as e:
        logger.warning(f"ITS analysis failed: {e}")
        return {"level_change": None, "trend_change": None, "p_value": None,
                "r_squared": None, "error": str(e)}
