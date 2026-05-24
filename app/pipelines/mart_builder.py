from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any
import logging

logger = logging.getLogger(__name__)

JOOLA_BRAND_ID = "04db8591-37a3-4634-9d11-536975fa6935"


def week_monday(date_str: str) -> str:
    """Return the ISO Monday (YYYY-MM-DD) for any date string."""
    d = datetime.fromisoformat(date_str[:10])
    weekday = d.weekday()  # 0=Mon, 6=Sun
    monday = d - timedelta(days=weekday)
    return monday.strftime("%Y-%m-%d")


def yt_week_to_monday(year: int, week_num: int) -> str:
    """Convert YouTube year+week_number to ISO Monday."""
    jan4 = date(year, 1, 4)
    dow = jan4.weekday()
    week1_mon = jan4 - timedelta(days=dow)
    target = week1_mon + timedelta(weeks=week_num - 1)
    return target.strftime("%Y-%m-%d")


@dataclass
class MartRow:
    brand_id: str
    week_start: str
    platform: str
    metric_name: str
    value: float
    source_table: str
    row_count: int = 1

    def to_dict(self) -> dict:
        return {
            "brand_id": self.brand_id,
            "week_start": self.week_start,
            "platform": self.platform,
            "metric_name": self.metric_name,
            "value": self.value,
            "source_table": self.source_table,
            "row_count": self.row_count,
        }


class MartBuilder:
    @staticmethod
    def _ig_to_rows(brand_id: str, data: list[dict]) -> list[MartRow]:
        rows = []
        for r in data:
            if not r.get("week_start"):
                continue
            w = week_monday(r["week_start"])
            for metric, field, transform in [
                ("ig_views", "total_views", lambda v: v or 0),
                ("ig_posts", "posts_published", lambda v: v or 0),
                ("ig_engagement_rate", "avg_engagement_rate", lambda v: (v or 0) * 100),
                ("ig_purchase_intent", "purchase_intent_count", lambda v: v or 0),
                ("ig_complaints", "complaint_count", lambda v: v or 0),
            ]:
                rows.append(MartRow(brand_id, w, "instagram", metric, transform(r.get(field)), "joola_ig_weekly_snapshot"))
        return rows

    @staticmethod
    def _yt_to_rows(brand_id: str, data: list[dict]) -> list[MartRow]:
        rows = []
        for r in data:
            if not r.get("year") or not r.get("week_number"):
                continue
            w = yt_week_to_monday(r["year"], r["week_number"])
            rows.append(MartRow(brand_id, w, "youtube", "yt_views", r.get("total_views") or 0, "yt_channel_weekly"))
            rows.append(MartRow(brand_id, w, "youtube", "yt_videos_uploaded", r.get("videos_uploaded_this_week") or 0, "yt_channel_weekly"))
        return rows

    @staticmethod
    def _tiktok_to_rows(brand_id: str, data: list[dict]) -> list[MartRow]:
        weeks: dict[str, dict] = {}
        for v in data:
            if not v.get("posted_at"):
                continue
            w = week_monday(v["posted_at"])
            if w not in weeks:
                weeks[w] = {"videos": 0, "views": 0}
            weeks[w]["videos"] += 1
            weeks[w]["views"] += float(v.get("view_count") or 0)
        rows = []
        for w, agg in weeks.items():
            rows.append(MartRow(brand_id, w, "tiktok", "tt_videos", agg["videos"], "tiktok_videos"))
            rows.append(MartRow(brand_id, w, "tiktok", "tt_views", agg["views"], "tiktok_videos"))
        return rows

    @staticmethod
    def _reddit_to_rows(brand_id: str, data: list[dict]) -> list[MartRow]:
        weeks: dict[str, dict] = {}
        for m in data:
            if not m.get("posted_at"):
                continue
            w = week_monday(m["posted_at"])
            if w not in weeks:
                weeks[w] = {"mentions": 0, "upvotes": 0, "opportunity": 0}
            weeks[w]["mentions"] += 1
            weeks[w]["upvotes"] += m.get("upvotes") or 0
            if m.get("is_opportunity"):
                weeks[w]["opportunity"] += 1
        rows = []
        for w, agg in weeks.items():
            rows.append(MartRow(brand_id, w, "reddit", "rd_mentions", agg["mentions"], "reddit_mentions"))
            rows.append(MartRow(brand_id, w, "reddit", "rd_upvotes", agg["upvotes"], "reddit_mentions"))
            rows.append(MartRow(brand_id, w, "reddit", "rd_opportunity", agg["opportunity"], "reddit_mentions"))
        return rows

    @classmethod
    def build_all_rows(
        cls,
        brand_id: str,
        ig_data: list[dict],
        yt_data: list[dict],
        tt_data: list[dict],
        rd_data: list[dict],
    ) -> list[MartRow]:
        rows = []
        rows.extend(cls._ig_to_rows(brand_id, ig_data))
        rows.extend(cls._yt_to_rows(brand_id, yt_data))
        rows.extend(cls._tiktok_to_rows(brand_id, tt_data))
        rows.extend(cls._reddit_to_rows(brand_id, rd_data))
        return rows
