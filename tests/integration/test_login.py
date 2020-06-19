from fastapi.testclient import TestClient
import pytest

from backend.app import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_wrong_login(client):
    response = client.post(
        "/login",
        json=dict(
            username='john',
            password='fakepassword',
        ))
    assert response.status_code == 400
    assert response.json()['error'] == 'Invalid credentials'


def test_create_user(client):
    response = client.post(
        "/register_user",
        json=dict(
            username='realuser',
            password='rightpassword',
        ))
    assert response.status_code == 200

    response = client.post(
        "/register_user",
        json=dict(
            username='realuser',
            password='rightpassword',
        ))
    assert response.status_code == 409

    response = client.post(
        "/login",
        json=dict(
            username='realuser',
            password='wrongpassword',
        ))
    assert response.status_code == 400

    response = client.post(
        "/login",
        json=dict(
            username='realuser',
            password='rightpassword',
        ))
    assert response.status_code == 200
    response = client.get(
        "/login/whoami",
        )
    assert response.status_code == 200
    assert response.json() == {'authenticated': True, 'name': 'realuser'}
