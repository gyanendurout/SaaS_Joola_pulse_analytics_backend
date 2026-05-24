from dataclasses import dataclass, field
import numpy as np


ATTENTION_WEIGHTS = {
    "ig_views": 0.25,
    "yt_views": 0.20,
    "tt_views": 0.20,
    "rd_mentions": 0.20,
    "rd_upvotes": 0.15,
}

SALES_WEIGHTS = {
    "ig_purchase_intent": 0.40,
    "rd_opportunity": 0.30,
    "ig_engagement_rate": 0.30,
}


@dataclass
class ScoreRow:
    week_start: str
    attention_score: float
    sales_likelihood_score: float
    attention_components: dict = field(default_factory=dict)
    sales_components: dict = field(default_factory=dict)


def normalize_series(values: list[float]) -> list[float]:
    """Min-max normalization to [0, 1]. Returns zeros if all values equal."""
    arr = np.array(values, dtype=float)
    mn, mx = arr.min(), arr.max()
    if mx - mn < 1e-10:
        return [0.0] * len(values)
    return list((arr - mn) / (mx - mn))


def compute_composite_scores(
    weeks: list[str],
    metric_series: dict[str, list[float]],
) -> list[ScoreRow]:
    n = len(weeks)
    normalized: dict[str, list[float]] = {}
    for metric, values in metric_series.items():
        padded = values[:n] + [0.0] * max(0, n - len(values))
        normalized[metric] = normalize_series(padded)

    scores = []
    for i, week in enumerate(weeks):
        attention = sum(
            normalized.get(m, [0.0] * n)[i] * w
            for m, w in ATTENTION_WEIGHTS.items()
        ) * 100

        sales = sum(
            normalized.get(m, [0.0] * n)[i] * w
            for m, w in SALES_WEIGHTS.items()
        ) * 100

        scores.append(ScoreRow(
            week_start=week,
            attention_score=round(min(max(attention, 0.0), 100.0), 2),
            sales_likelihood_score=round(min(max(sales, 0.0), 100.0), 2),
            attention_components={m: round(normalized.get(m, [0.0] * n)[i] * 100, 1) for m in ATTENTION_WEIGHTS},
            sales_components={m: round(normalized.get(m, [0.0] * n)[i] * 100, 1) for m in SALES_WEIGHTS},
        ))
    return scores
