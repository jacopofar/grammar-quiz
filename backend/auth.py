from authlib.common.security import generate_token
from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI, HTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from backend.config import Config

config = Config()


def attach_auth(app: FastAPI):
    """Attach authentication endpoints to an app.

    These endpoints allow for login, logout and session check
    """
    app.add_middleware(SessionMiddleware, secret_key=config.secret_session_key)
    oauth = OAuth()
    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        },
        client_secret=config.sso_google_secret,
        client_id=config.sso_google_client_id,
    )

    @app.get("/login/login")
    async def login(request: Request):
        redirect_uri = request.url_for('auth')
        if 'X-Forwarded-Proto' in request.headers:
            redirect_uri = redirect_uri.replace(
              'http:', request.headers['X-Forwarded-Proto'] + ':')
        # additional security, nonce is random and validated in case the URL
        # is read but not the session cookie
        request.session['nonce'] = generate_token()

        return await oauth.google.authorize_redirect(
            request, redirect_uri, nonce=request.session['nonce'])

    @app.get('/login/auth')
    async def auth(request: Request):
        token = await oauth.google.authorize_access_token(request)
        user = await oauth.google.parse_id_token(request, token)
        if user['nonce'] != request.session['nonce']:
            raise HTTPException(
                status_code=401, detail="Wrong nonce value, weird...")
        # here check the user mail, or even better an hash of it, and store the id
        request.session['name'] = user['name']
        del request.session['nonce']
        return RedirectResponse(url='/')

    @app.post('/login/logout')
    async def logout(request: Request):
        if 'name' in request.session:
            del request.session['name']
        if 'id' in request.session:
            del request.session['id']
        return dict(logout=True)

    @app.get('/login/whoami')
    async def whoami(request: Request):
        if 'name' not in request.session:
            return dict(authenticated=False)
        return dict(
            authenticated=True,
            name=request.session['name'],
          )
