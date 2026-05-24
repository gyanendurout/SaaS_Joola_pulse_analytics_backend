from app.agents.base import BaseAnalyticsAgent

SYSTEM = """You are a sports brand marketing analyst. Given JOOLA's weekly attention score and sales likelihood score, write 2 sentences explaining what's driving the numbers and what the marketing team should focus on this week."""


class CompositeScoreAgent(BaseAnalyticsAgent):
    async def interpret(self, data: dict) -> str:
        user = (
            f"Week: {data.get('week_start')}\n"
            f"Attention score: {data.get('attention_score', 0):.1f}/100\n"
            f"Sales likelihood: {data.get('sales_likelihood_score', 0):.1f}/100\n"
            f"Top attention drivers: {data.get('attention_components', {})}\n"
            f"Top sales drivers: {data.get('sales_components', {})}"
        )
        return await self._call(SYSTEM, user)
