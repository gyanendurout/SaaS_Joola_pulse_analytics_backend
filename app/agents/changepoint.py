from app.agents.base import BaseAnalyticsAgent

SYSTEM = """You are a sports brand marketing analyst. Given a changepoint detected in JOOLA's social media metrics, provide a short label (5-8 words) describing the likely business cause. Examples: "Product launch buzz", "Tournament weekend spike", "Campaign engagement lift". Return ONLY the label, no explanation."""


class ChangepointLabelAgent(BaseAnalyticsAgent):
    async def interpret(self, data: dict) -> str:
        return await self.label_changepoint(data)

    async def label_changepoint(self, data: dict) -> str:
        user = (
            f"Metric: {data.get('metric')}\n"
            f"Week: {data.get('changepoint_week')}\n"
            f"Change: {data.get('direction')} {abs(data.get('pct_change', 0)):.1f}%\n"
            f"Pre-mean: {data.get('pre_mean', 0):.0f} → Post-mean: {data.get('post_mean', 0):.0f}"
        )
        return await self._call(SYSTEM, user, max_tokens=32)
