"""Database connection and conversation management for the backend."""

import os
from functools import lru_cache
from pathlib import Path
from collections.abc import Iterator

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Set DATABASE_URL in backend/.env or the environment")
    return url


@lru_cache(maxsize=1)
def database_engine() -> Engine:
    return create_engine(database_url(), pool_pre_ping=True, hide_parameters=True)


def get_db() -> Iterator[Session]:
    with Session(database_engine()) as session:
        yield session
