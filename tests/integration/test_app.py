from fastapi.testclient import TestClient
import pytest

from backend.app import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_get_languages(client):
    languages = client.get("/languages").json()
    assert len(languages) > 0
    assert 'iso693_3' in languages[0]
    # the codes are always 3 letters
    assert len(languages[0]['iso693_3']) == 3
    assert 'name' in languages[0]


def test_draw_cards(client):
    response = client.post(
        "/draw_cards",
        json=dict(
            target_lang='deu',
            source_langs=['eng', 'jap'],
        ))
    assert len(response.json()) == 10
