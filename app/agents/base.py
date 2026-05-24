from abc import ABC, abstractmethod
from openai import AsyncOpenAI


class BaseAnalyticsAgent(ABC):
    def __init__(self, client: AsyncOpenAI, model: str):
        self.client = client
        self.model = model

    async def _call(self, system: str, user: str, max_tokens: int = 512) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return response.choices[0].message.content.strip()

    @abstractmethod
    async def interpret(self, data: dict) -> str: ...
