import logging
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from backend.dbutil import get_conn, attach_db_cycle
from backend.auth import attach_auth

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

app = FastAPI()

attach_db_cycle(app)
attach_auth(app)

# TODO later use a reverse proxy to serve static files
# this works perfectly for now
app.mount(
    "/app",
    StaticFiles(
        directory=Path(__file__).parent / "static",
        check_dir=False,
        html=True),
    name="app_files"
)

@app.get("/")
def index():
    """Redirect the user to the static app."""
    return RedirectResponse(url="/app")


@app.get("/languages")
async def get_languages():
    """Return list of all available languages."""
    async with get_conn() as conn:
        return await conn.fetch("""
            SELECT iso693_3, name FROM language
            """)


class QuizRequest(BaseModel):
    source_langs: List[str]
    target_lang: str


@app.post("/draw_cards")
async def draw_cards(qr: QuizRequest):
    """Return the cards to test for this session.

    The selection contains both old cards to renew and a given number of
    brand new cards.
    """
    # fake constant user id to simplify multi-user later
    current_user = 1
    # TODO would be nice to move queries to .sql files referred by name
    # and have a concise helper for that.
    async with get_conn() as conn:
        cards = await conn.fetch(
            """
            SELECT * FROM (
              SELECT
                  fl.name     AS from_language,
                  tl.name     AS to_language,
                  c.from_id   AS from_id,
                  c.to_id     AS to_id,
                  c.from_txt  AS from_txt,
                  c.to_tokens AS to_tokens
              FROM
                  card c
                      JOIN language fl
                          ON fl.id = c.from_lang
                      JOIN language tl
                          ON tl.id = c.to_lang
                      LEFT JOIN card_user_state cus
                              ON c.from_id = cus.from_id
                                  AND c.to_id = cus.to_id
                                  AND cus.account_id = $3
              WHERE
                  fl.iso693_3 = ANY($2)
                  AND tl.iso693_3 = $1
                  AND cus.account_id IS NULL
              LIMIT 20
            ) newcards

            UNION ALL

            SELECT
                fl.name     AS from_language,
                tl.name     AS to_language,
                c.from_id   AS from_id,
                c.to_id     AS to_id,
                c.from_txt  AS from_txt,
                c.to_tokens AS to_tokens
            FROM
                card c
                    JOIN language fl
                        ON fl.id = c.from_lang
                    JOIN language tl
                        ON tl.id = c.to_lang
                    JOIN card_user_state cus
                            ON c.from_id = cus.from_id
                                AND c.to_id = cus.to_id
                                AND cus.account_id = $3
                                AND cus.next_review < current_timestamp
            WHERE
                fl.iso693_3 = ANY($2)
                AND tl.iso693_3 = $1
            """,
            qr.target_lang,
            qr.source_langs,
            current_user)
        return cards


class CardAnswer(BaseModel):
    from_id: int
    to_id: int
    expected_answers: List[str]
    given_answers:  List[str]
    correct: bool
    repetition: bool


@app.post("/register_answer")
async def register_answer(ans: CardAnswer):
    """Register the answer an user gave to a card.

    This is used both to decide whether and when to show the card again and to
    collect information about which words and sentences are hard and which
    mistakes are the most common.
    """
    # fake constant user id to simplify multi-user later
    current_user = 1
    async with get_conn() as conn:
        # repetitions in the same session do not affect further the state
        if not ans.repetition:
            if ans.correct:
                # not correct, roughly equivalent to "Easy" in Anki
                # EF = EF + 0.15
                #  if new, EF is 2.5 + 0.15 = 2.65
                # I = 1 iif new card
                # I = 6 iif I = 1
                # I = round(I * EF) iif I > 1 and not new card
                # next review in I days
                await conn.execute(
                    """
                    INSERT INTO card_user_state AS cus(
                      from_id,
                      to_id,
                      account_id,
                      next_review,
                      i_factor,
                      ef_factor
                      )
                    VALUES (
                      $1,
                      $2,
                      $3,
                      current_timestamp + '1 day' :: INTERVAL,
                      1,
                      2.65
                      )
                    ON CONFLICT (from_id, to_id, account_id) DO UPDATE SET
                      next_review = current_timestamp + ROUND(cus.i_factor) * '1 day' :: interval,
                      i_factor = CASE
                            WHEN cus.i_factor = 1 THEN 6
                            ELSE round(cus.i_factor * cus.ef_factor) END,
                      ef_factor = GREATEST(1.3, cus.ef_factor + 0.15)
                    """,
                    ans.from_id,
                    ans.to_id,
                    current_user
                )
            else:
                # not correct, roughly equivalent to "Again" in Anki
                # EF = max(1.3, EF - 0.2)
                #  if new, EF is assumed 2.5, so will become 2.5 - 0.2 = 2.3
                # I = 1
                await conn.execute(
                    """
                     INSERT INTO card_user_state AS cus(
                      from_id,
                      to_id,
                      account_id,
                      next_review,
                      i_factor,
                      ef_factor
                      )
                    VALUES (
                      $1,
                      $2,
                      $3,
                      current_timestamp + '1 day' :: INTERVAL,
                      1,
                      2.3
                      )
                    ON CONFLICT (from_id, to_id, account_id) DO UPDATE SET
                      next_review = current_timestamp + '1 day' :: INTERVAL,
                      i_factor = 1,
                      ef_factor = GREATEST(1.3, cus.ef_factor)
                    """,
                    ans.from_id,
                    ans.to_id,
                    current_user
                )
        await conn.execute(
            """
            INSERT INTO revlog (
              from_id,
              to_id,
              account_id,
              review_time,
              answers,
              expected_answers,
              correct
              )
            VALUES ($1, $2, $3, current_timestamp, $4, $5, $6)
            """,
            ans.from_id,
            ans.to_id,
            current_user,
            ans.given_answers,
            ans.expected_answers,
            ans.correct
        )
        return 'OK'
