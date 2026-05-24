import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def _make_mock_db():
    mock_db = MagicMock()
    empty = MagicMock()
    empty.data = []
    # Chain stubs for common query patterns
    mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = empty
    mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = empty
    mock_db.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = empty
    mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = empty
    mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value = empty
    return mock_db


@pytest.fixture
def client():
    mock_db = _make_mock_db()
    with patch("app.database.get_db", return_value=mock_db), \
         patch("app.scheduler.jobs.start_scheduler"), \
         patch("app.scheduler.jobs.stop_scheduler"):
        from app.main import app
        with TestClient(app, raise_server_exceptions=True) as tc:
            yield tc


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_timeseries_endpoint_exists(client):
    response = client.get("/api/timeseries")
    assert response.status_code == 200
    assert "data" in response.json()


def test_correlation_endpoint_exists(client):
    response = client.get("/api/correlation")
    assert response.status_code == 200
    assert "data" in response.json()


def test_composite_endpoint_exists(client):
    response = client.get("/api/composite-scores")
    assert response.status_code == 200
    assert "data" in response.json()


def test_runs_endpoint_exists(client):
    response = client.get("/api/runs")
    assert response.status_code == 200
    assert "data" in response.json()


def test_events_endpoint_exists(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    assert "data" in response.json()


def test_granger_endpoint_exists(client):
    response = client.get("/api/granger")
    assert response.status_code == 200
    assert "data" in response.json()


def test_changepoints_endpoint_exists(client):
    response = client.get("/api/changepoints")
    assert response.status_code == 200
    assert "data" in response.json()
