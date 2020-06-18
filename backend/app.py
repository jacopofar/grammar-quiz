from hashlib import sha256
import logging
from pathlib import Path
import secrets
import string
from typing import List

from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse

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
async def draw_cards(qr: QuizRequest, request: Request):
    """Return the cards to test for this session.

    The selection contains both old cards to renew and a given number of
    brand new cards.
    """
    current_user = request.session.get('id', 1)

    # TODO would be nice to move queries to .sql files referred by name
    # and have a concise helper for that.
    async with get_conn() as conn:
        cards = await conn.fetch(
            """
            SELECT * FROM (
              SELECT
                  fl.name         AS from_language,
                  tl.name         AS to_language,
                  fl.iso693_3     AS from_language_code,
                  tl.iso693_3     AS to_language_code,
                  c.from_id       AS from_id,
                  c.to_id         AS to_id,
                  c.from_txt      AS from_text,
                  c.to_tokens     AS to_tokens,
                  c.original_txt  AS to_text
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
                      LEFT JOIN card_trouble tro
                             ON c.from_id = tro.from_id
                                  AND c.to_id = tro.to_id
                                  AND tro.account_id = $3
              WHERE
                  fl.iso693_3 = ANY($2)
                  AND tl.iso693_3 = $1
                  AND cus.account_id IS NULL
                  AND tro.account_id IS NULL
              LIMIT 20
            ) newcards

            UNION ALL

            SELECT
                fl.name         AS from_language,
                tl.name         AS to_language,
                fl.iso693_3     AS from_language_code,
                tl.iso693_3     AS to_language_code,
                c.from_id       AS from_id,
                c.to_id         AS to_id,
                c.from_txt      AS from_text,
                c.to_tokens     AS to_tokens,
                c.original_txt  AS to_text
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
async def register_answer(ans: CardAnswer, request: Request):
    """Register the answer an user gave to a card.

    This is used both to decide whether and when to show the card again and to
    collect information about which words and sentences are hard and which
    mistakes are the most common.
    """
    current_user = request.session.get('id', 1)
    async with get_conn() as conn:
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
        # user 1 is the anonymous user, so there's no revision time update
        if current_user == 1:
            return 'OK'
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


class IssueReport(BaseModel):
    description: str
    from_id: int
    to_id: int
    issue_type: str


@app.post("/report_issue")
async def report_issue(issue: IssueReport, request: Request):
    current_user = request.session.get('id', 1)
    async with get_conn() as conn:
        await conn.fetchrow(
            """
            INSERT INTO card_trouble (
                from_id, to_id, account_id, ts, description, issue_type)
            VALUES
                ($1, $2, $3, current_timestamp, $4, $5)
            """,
            issue.from_id,
            issue.to_id,
            current_user,
            issue.description,
            issue.issue_type,
            )
        if current_user != 1:
            await conn.execute(
                """
                DELETE FROM card_user_state
                WHERE
                    from_id = $1
                    AND to_id = $2
                    AND account_id = $3
                """,
                issue.from_id,
                issue.to_id,
                current_user,
            )
    return 'OK'


class UserCreationRequest(BaseModel):
    username: str
    password: str


@app.post("/register_user")
async def register_user(cred: UserCreationRequest, request: Request):
    """Register the user.

    Sets the session and return OK when the user could be created,
    or return a JSON with the error field describing the problem.
    """
    async with get_conn() as conn:
        found = await conn.fetchrow(
            """
            SELECT 1 FROM
                account_internal
                WHERE username = $1
            """,
            cred.username)
        if found is not None:
            return JSONResponse(
                dict(error='An user with this name already exists'),
                status_code=status.HTTP_409_CONFLICT,
            )
        alphabet = string.ascii_letters + string.digits
        salt = ''.join(secrets.choice(alphabet) for i in range(8))
        hs = sha256((cred.password + salt).encode('utf-8')).hexdigest()
        res = await conn.fetchrow(
            """
            INSERT INTO account_internal(
                username,
                password_hash,
                password_salt)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            cred.username,
            hs,
            salt)
        id_ = res['id']
        request.session['name'] = cred.username
        request.session['id'] = id_
        return 'OK'


# identical to creation request, but keeping the name was confusing
class UserLoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(cred: UserLoginRequest, request: Request):
    """Login an user

    Sets the session and return OK when the user could log in,
    or return a JSON with the error field describing the problem.
    """
    async with get_conn() as conn:
        found = await conn.fetchrow(
            """
            SELECT id, password_hash, password_salt FROM
                account_internal
                WHERE username = $1
            """,
            cred.username)
        if found is None:
            return JSONResponse(
                dict(error='Invalid credentials'),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        hs = sha256(
            (cred.password + found['password_salt']).encode('utf-8')
            ).hexdigest()
        if hs == found['password_hash']:
            request.session['name'] = cred.username
            request.session['id'] = found['id']
            return 'OK'
        else:
            return JSONResponse(
                dict(error='Invalid credentials'),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
