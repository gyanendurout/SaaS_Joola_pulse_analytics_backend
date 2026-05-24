import json
from app.agents.base import BaseAnalyticsAgent

SYSTEM = """You are the Chief Marketing Intelligence Officer for JOOLA pickleball brand. Given a week's worth of analytical results across all social platforms, write a concise executive summary with:
1. A punchy title (max 10 words)
2. A 3-4 sentence narrative of the week's key signals
3. 3-5 bullet point key_points as a JSON array of strings

Respond in JSON format:
{"title": "...", "body": "...", "key_points": ["...", "..."]}"""


class WeeklyNarrativeAgent(BaseAnalyticsAgent):
    async def interpret(self, data: dict) -> str:
        return await self.generate_summary(data)

    async def generate_summary(self, data: dict) -> dict:
        user = f"Weekly analytics for {data.get('week_start')}:\n{json.dumps(data, indent=2)[:3000]}"
        raw = await self._call(SYSTEM, user, max_tokens=1024)
        cleaned = raw.strip()
        # Strip markdown code fences (```json ... ```) that gpt-4o sometimes wraps JSON in
        if cleaned.startswith('```'):
            lines = cleaned.split('\n')
            end = len(lines)
            for i in range(len(lines) - 1, 0, -1):
                if lines[i].strip() == '```':
                    end = i
                    break
            cleaned = '\n'.join(lines[1:end]).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"title": "Weekly Insights", "body": raw, "key_points": []}
