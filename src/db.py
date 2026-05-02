"""Database utilities — connection helper and raw schema setup."""

from contextlib import contextmanager
from typing import Generator

import psycopg2
from loguru import logger

from src.config import db_config


@contextmanager
def get_connection() -> Generator:
    """Yield a psycopg2 connection that auto-closes on exit."""
    conn = psycopg2.connect(db_config.connection_string)
    try:
        yield conn
    finally:
        conn.close()


def ensure_raw_schema() -> None:
    """Create the raw schema if it does not exist."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
            conn.commit()
    logger.info("Schema 'raw' is ready.")
