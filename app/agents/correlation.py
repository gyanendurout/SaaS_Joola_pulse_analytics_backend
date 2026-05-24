from app.agents.base import BaseAnalyticsAgent

SYSTEM = """You are a sports brand marketing analyst. Given correlation data between social media metrics for JOOLA pickleball brand, write 2-3 sentences explaining the most important business relationship in plain English. Focus on what it means for marketing decisions. Be specific about which metrics correlate and what action JOOLA should take."""


class CorrelationInterpreterAgent(BaseAnalyticsAgent):
    async def interpret(self, data: dict) -> str:
        top_pairs = data.get("top_pairs", [])
        if not top_pairs:
            return "Insufficient data to identify correlation patterns."
        user = "Top correlating metric pairs:\n" + "\n".join(
            f"- {p['metric_a']} ↔ {p['metric_b']}: r={p['pearson_r']:.2f}"
            for p in top_pairs[:5]
        )
        return await self._call(SYSTEM, user)
