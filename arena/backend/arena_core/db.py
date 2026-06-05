"""Database engine + session factory.

SQLite by default (dev/test); Postgres in production via the DATABASE_URL env var
(SQLAlchemy makes the model code portable across both).
"""
from __future__ import annotations

import os

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Deterministic constraint/index names so Alembic autogenerate is stable across runs.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def make_engine(url: str | None = None):
    url = url or os.environ.get("DATABASE_URL", "sqlite:///./arena.db")
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False}, future=True)
    # Postgres (prod): pre-ping drops connections a long-idle worker may be holding.
    return create_engine(url, pool_pre_ping=True, future=True)


def make_session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)


def init_db(engine):
    # import models so they register on Base.metadata, then create tables
    from . import models  # noqa: F401
    Base.metadata.create_all(engine)
