import logging
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from backend.dbutil import get_conn, attach_db_cycle

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


app = FastAPI()
attach_db_cycle(app)

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


@app.get("/current_time")
async def current_time():
    """Return current time, as an example."""
    async with get_conn() as conn:
        now = await conn.fetchrow("""
            SELECT date_trunc('second', current_timestamp) AS now_ts
            """)
        return now['now_ts']


class QuizRequest(BaseModel):
    source_langs: List[str]
    target_lang: str


@app.post("/draw_cards")
async def draw_cards(qr: QuizRequest):
    """Return a bunch of random cards."""
    # fake constant user id to simplify multi-user later
    current_user = 1
    # TODO would be nice to move queries to .sql files referred by name
    # and have a concise helper for that.
    async with get_conn() as conn:
        cards = await conn.fetch(
            """
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
                            ON c.from_id = cus.from_id AND c.to_id = cus.to_id
                                AND cus.account_id = $3
            WHERE
                fl.iso693_3 = ANY($2)
            AND tl.iso693_3 = $1
            AND cus.account_id IS NULL
            LIMIT 10
            """,
            qr.target_lang,
            qr.source_langs,
            current_user)
        return cards
