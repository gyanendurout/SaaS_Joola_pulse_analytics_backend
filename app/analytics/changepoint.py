from dataclasses import dataclass
import numpy as np
import ruptures as rpt


MIN_SIGNAL_LENGTH = 8


@dataclass
class ChangePoint:
    index: int
    pre_mean: float
    post_mean: float
    pct_change: float
    direction: str  # "increase" or "decrease"


def detect_changepoints(
    signal: list[float],
    min_size: int = 4,
    penalty: str = "bic",
) -> list[ChangePoint]:
    """Detect changepoints using PELT algorithm (ruptures library)."""
    if len(signal) < MIN_SIGNAL_LENGTH:
        return []

    arr = np.array(signal, dtype=float)
    if arr.std() < 1e-10:
        return []

    try:
        algo = rpt.Pelt(model="l2", min_size=min_size).fit(arr)
        breakpoints = algo.predict(pen=3)
        breakpoints = [b for b in breakpoints if b < len(signal)]
    except Exception:
        return []

    result = []
    prev = 0
    for bp in breakpoints:
        pre_segment = arr[prev:bp]
        post_segment = arr[bp:]
        if len(pre_segment) == 0 or len(post_segment) == 0:
            continue
        pre_mean = float(pre_segment.mean())
        post_mean = float(post_segment.mean())
        if abs(pre_mean) < 1e-10:
            pct_change = 0.0
        else:
            pct_change = (post_mean - pre_mean) / abs(pre_mean) * 100
        result.append(ChangePoint(
            index=bp,
            pre_mean=pre_mean,
            post_mean=post_mean,
            pct_change=pct_change,
            direction="increase" if pct_change >= 0 else "decrease",
        ))
        prev = bp

    return result
