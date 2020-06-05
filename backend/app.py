import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
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

