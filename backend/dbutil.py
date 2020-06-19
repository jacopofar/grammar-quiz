from contextlib import asynccontextmanager
from functools import lru_cache
import importlib.resources as pkg_resources
import logging

import asyncpg
from fastapi import FastAPI

import backend.sql
from backend.config import Config

config = Config()

__db_pool: asyncpg.pool.Pool = None

logger = logging.getLogger()


def attach_db_cycle(app: FastAPI):
    @app.on_event("startup")
    async def on_app_startup():
        global __db_pool
        logger.debug('App did startup, creating connection pool')
        __db_pool = await asyncpg.create_pool(
            dsn=config.pg_conn_str,
            command_timeout=10
            )

    @app.on_event("shutdown")
    async def on_app_shutdown():
        logger.debug('App shutting down, terminating connection pool')
        __db_pool.terminate()


@asynccontextmanager
async def get_conn():
    conn = await __db_pool.acquire()
    try:
        yield conn
    finally:
        await __db_pool.release(conn)


@lru_cache()
def get_sql(query_name: str) -> str:
    """Read the content of a stored query as a string.

    SQL comments are stripped.
    """
    query = pkg_resources.read_text(
        backend.sql, f'{query_name}.sql').split('\n')
    query = [line for line in query if not line.startswith('--')]
    return '\n'.join(query)
