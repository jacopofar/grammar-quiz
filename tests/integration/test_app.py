from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_read_main():
    print(app)
    response = client.get("/current_time")
    assert len(response.json()) == len('2020-06-04T19:13:50.905232')
    assert response.text[5] == '-'
