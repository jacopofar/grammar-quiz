from pydantic import (
    BaseSettings, PostgresDsn, Field
)


class Config(BaseSettings):
    pg_conn_str: PostgresDsn = Field(..., env='PG_CONN_STR')
    sso_google_client_id: str = Field(..., env='SSO_GOOGLE_CLIENT_ID')
    sso_google_secret: str = Field(..., env='SSO_GOOGLE_SECRET')
    secret_session_key: str = Field(..., env='SECRET_SESSION_KEY')


