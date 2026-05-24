import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []
    db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
    db.table.return_value.insert.return_value.execute.return_value.data = [{"id": "test-uuid"}]
    db.table.return_value.upsert.return_value.execute.return_value.data = []
    return db


@pytest.fixture
def mock_anthropic_client():
    client = MagicMock()
    client.messages = MagicMock()
    client.messages.create = AsyncMock(return_value=MagicMock(
        content=[MagicMock(text="Test AI narrative response.")]
    ))
    return client
