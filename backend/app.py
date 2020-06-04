import logging
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

app = FastAPI()
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
def current_time():
    """Return current time, as an example."""
    return datetime.now().isoformat()
