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


def test_answer_then_redraw(client):
    initial_cards = client.post(
        "/draw_cards",
        json=dict(
            target_lang='deu',
            source_langs=['eng', 'jap'],
        ))
    second_draw = client.post(
        "/draw_cards",
        json=dict(
            target_lang='deu',
            source_langs=['eng', 'jap'],
        ))
    # drawing the cards is not affecting their availability
    assert len(initial_cards.json()) > 1
    assert len(initial_cards.json()) == len(second_draw.json())

    card1 = second_draw.json()[0]
    card2 = second_draw.json()[1]

    # send a correct answer
    ok_response = client.post(
        "/register_answer",
        json=dict(
            from_id=card1['from_id'],
            to_id=card1['to_id'],
            expected_answers=['SOME', 'token'],
            given_answers=['some', 'token'],
            correct=True,
            repetition=False,
        ))
    assert ok_response.json() == 'OK'
    # send a wrong answer
    ok_response = client.post(
        "/register_answer",
        json=dict(
            from_id=card2['from_id'],
            to_id=card2['to_id'],
            expected_answers=['another', 'token'],
            given_answers=['wrong', 'stuff'],
            correct=False,
            repetition=False,
        ))
    assert ok_response.json() == 'OK'
    draw_after = client.post(
        "/draw_cards",
        json=dict(
            target_lang='deu',
            source_langs=['eng', 'jap'],
        ))
    cards = [
        (card['from_id'], card['to_id'])
        for card in draw_after.json()
    ]
    # TODO they are, because the test user is anonymous and so is stateless
    # # the answers we already sent are not in the new selection
    # assert (card1['from_id'], card1['to_id']) not in cards
    # assert (card2['from_id'], card2['to_id']) not in cards
