import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agents.base import BaseAnalyticsAgent
from app.agents.correlation import CorrelationInterpreterAgent
from app.agents.changepoint import ChangepointLabelAgent
from app.agents.composite import CompositeScoreAgent
from app.agents.narrative import WeeklyNarrativeAgent


def _make_openai_mock(text: str) -> MagicMock:
    """Build a mock that matches openai.AsyncOpenAI chat.completions.create response shape."""
    message = MagicMock()
    message.content = text
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    client = MagicMock()
    client.chat = MagicMock()
    client.chat.completions = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=response)
    return client


@pytest.fixture
def mock_openai():
    return _make_openai_mock(
        "Instagram views strongly predict YouTube views with a 2-week lag."
    )


@pytest.fixture
def mock_json_openai():
    return _make_openai_mock(
        '{"title": "Strong Week", "body": "Good signals.", "key_points": ["Point 1"]}'
    )


@pytest.mark.asyncio
async def test_correlation_agent_returns_string(mock_openai):
    agent = CorrelationInterpreterAgent(mock_openai, model="gpt-4o-mini")
    result = await agent.interpret({
        "top_pairs": [{"metric_a": "ig_views", "metric_b": "yt_views", "pearson_r": 0.82}]
    })
    assert isinstance(result, str)
    assert len(result) > 10


@pytest.mark.asyncio
async def test_changepoint_agent_returns_label(mock_openai):
    agent = ChangepointLabelAgent(mock_openai, model="gpt-4o-mini")
    result = await agent.label_changepoint({
        "metric": "ig_views",
        "changepoint_week": "2026-03-15",
        "pct_change": 45.2,
        "direction": "increase",
        "pre_mean": 10000,
        "post_mean": 14500,
    })
    assert isinstance(result, str)
    assert len(result) > 5


@pytest.mark.asyncio
async def test_base_agent_calls_openai(mock_openai):
    class TestAgent(BaseAnalyticsAgent):
        async def interpret(self, data: dict) -> str:
            return await self._call(system="You are a test agent.", user=str(data))

    agent = TestAgent(mock_openai, model="gpt-4o-mini")
    result = await agent.interpret({"test": "data"})
    assert mock_openai.chat.completions.create.called
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_correlation_agent_empty_data(mock_openai):
    agent = CorrelationInterpreterAgent(mock_openai, model="gpt-4o-mini")
    result = await agent.interpret({"top_pairs": []})
    assert "Insufficient" in result


@pytest.mark.asyncio
async def test_narrative_agent_returns_dict(mock_json_openai):
    agent = WeeklyNarrativeAgent(mock_json_openai, model="gpt-4o")
    result = await agent.generate_summary({"week_start": "2026-05-19", "attention_score": 65})
    assert isinstance(result, dict)
    assert "title" in result
    assert "body" in result
    assert "key_points" in result
