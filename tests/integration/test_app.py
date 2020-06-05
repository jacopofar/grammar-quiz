from fastapi.testclient import TestClient
import pytest

from backend.app import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_db_main(client):
    response = client.get("/current_time")
    assert len(response.json()) == len('2020-06-05T06:27:18+00:00')
    assert response.text[5] == '-'
