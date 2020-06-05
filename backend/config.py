from pydantic import (
    BaseSettings, PostgresDsn, Field
)


class Config(BaseSettings):
    pg_conn_str: PostgresDsn = Field(..., env='PG_CONN_STR')
