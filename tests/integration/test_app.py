from fastapi.testclient import TestClient
import pytest

from backend.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_read_main(client):
    response = client.get("/current_time")
    assert len(response.json()) == len('2020-06-04T19:13:50.905232')
    assert response.text[5] == '-'
