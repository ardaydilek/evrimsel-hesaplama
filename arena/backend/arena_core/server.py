"""Production server entrypoint: `uvicorn arena_core.server:build_prod_app --factory`.

Wires the FastAPI app (the same `create_app` factory used in dev/tests) to a Postgres
session factory (DATABASE_URL) and the real RQ-backed enqueue (REDIS_URL). Unlike the
dev entrypoint (app.py), this does NOT create tables — Alembic owns the schema (the M6
Alembic migration step / compose `migrate` service runs `alembic upgrade head` before the
API starts).
"""
from __future__ import annotations

from .api import create_app
from .db import make_engine, make_session_factory
from .worker import make_enqueue, make_queue


def build_prod_app():
    engine = make_engine()                       # DATABASE_URL -> Postgres
    session_factory = make_session_factory(engine)
    enqueue = make_enqueue(make_queue())         # REDIS_URL -> RQ queue
    return create_app(session_factory=session_factory, enqueue=enqueue)
