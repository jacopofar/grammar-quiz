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

from backend.dbutil import get_conn, attach_db_cycle, get_sql
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
async def get_languages(request: Request):
    """Return list of all available languages and latest used ones."""
    current_user = request.session.get('id', 1)

    async with get_conn() as conn:
        langs = await conn.fetch("""
            SELECT iso693_3, name FROM language
            """)
        latest = await conn.fetchrow(
            """
            SELECT
                src_langs, tgt_lang
            FROM latest_language
                WHERE account_id = $1
            """,
            current_user)
        if latest is None:
            return dict(languages=langs)
        else:
            return dict(languages=langs, selected=latest)


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

    async with get_conn() as conn:
        cards_new = await conn.fetch(
            get_sql('draw_new_cards'),
            qr.target_lang,
            qr.source_langs,
            current_user)
        if current_user == 1:
            return cards_new

        # store the selected language so next time the menu can show it directly
        await conn.execute(
            'DELETE FROM latest_language WHERE account_id=$1', current_user)
        await conn.execute(
            """
            INSERT INTO latest_language(
                account_id, src_langs, tgt_lang
                ) VALUES ($1, $2, $3)""",
            current_user,
            qr.source_langs,
            qr.target_lang
                )
        expired_cards = await conn.fetch(
            get_sql('get_expired_cards'),
            current_user)
        # TODO postgres insists in merging cards and languages before the join
        # with the user card state which is very selective
        # this is a workaround, the join is done in the backend
        languages_l = await conn.fetch(
            'SELECT id, name, iso693_3 FROM language')
        src_langs = {}
        to_lang_id = set()
        to_lang_name = None
        for l in languages_l:
            if l['iso693_3'] == qr.target_lang:
                to_lang_id = l['id']
                to_lang_name = l['name']

            if l['iso693_3'] in qr.source_langs:
                src_langs[l['id']] = (l['iso693_3'], l['name'])

        expired_cards = [
            dict(ec.items()) for ec in expired_cards
            if ec['from_lang'] in src_langs and ec['to_lang'] == to_lang_id]

        for ec in expired_cards:
            ec['from_language_code'] = src_langs[ec['from_lang']][0]
            ec['from_language'] = src_langs[ec['from_lang']][1]

            ec['to_language_code'] = qr.target_lang
            ec['to_language'] = to_lang_name

            del ec['from_lang']
            del ec['to_lang']

        return expired_cards + cards_new


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

    This is used both to decide whether and when to show the card again and
    to collect information about which words and sentences are hard and which
    mistakes are the most common.
    """
    current_user = request.session.get('id', 1)
    async with get_conn() as conn:
        await conn.execute(
            get_sql('insert_revlog'),
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
                # correct, roughly equivalent to "Easy" in Anki
                # EF = EF + 0.15
                #  if new, EF is 2.5 + 0.15 = 2.65
                # I = 1 iif new card
                # I = 6 iif I = 1
                # I = round(I * EF) iif I > 1 and not new card
                # next review in I days
                await conn.execute(
                    get_sql('reschedule_correct_card'),
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
                    get_sql('reschedule_wrong_card'),
                    ans.from_id,
                    ans.to_id,
                    current_user
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


class NoteAboutCard(BaseModel):
    from_id: int
    to_id: int
    hint: str
    explanation: str


@app.post("/take_note")
async def take_note(note: NoteAboutCard, request: Request):
    """Store a note about a card.

    The user can register a note about a card, to be shown next time they
    get the same sentence.
    There are two notes: the hint, which is shown before an answer, and the
    explanation, shown after.
    """
    current_user = request.session.get('id', 1)
    if current_user == 1:
        return JSONResponse(
            dict(error='Not logged in, cannot take notes'),
            status_code=status.HTTP_403_UNAUTHORIZED,
        )
    async with get_conn() as conn:
        await conn.execute(
            get_sql('upsert_card_notes'),
            note.from_id,
            note.to_id,
            current_user,
            note.hint,
            note.explanation,
        )
