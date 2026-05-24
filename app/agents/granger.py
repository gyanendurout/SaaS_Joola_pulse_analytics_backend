from app.agents.base import BaseAnalyticsAgent

SYSTEM = """You are a sports brand marketing analyst. Given Granger causality test results for JOOLA pickleball brand's social media data, explain the causal relationship in business terms. Mention the lag in weeks and what marketing action this suggests. 2 sentences max."""


class GrangerInterpreterAgent(BaseAnalyticsAgent):
    async def interpret(self, data: dict) -> str:
        cause = data.get("cause_metric", "unknown")
        effect = data.get("effect_metric", "unknown")
        lag = data.get("optimal_lag", "?")
        p = data.get("p_value", 1.0)
        user = f"Granger causality: {cause} → {effect}, lag={lag} weeks, p={p:.3f}"
        return await self._call(SYSTEM, user)
