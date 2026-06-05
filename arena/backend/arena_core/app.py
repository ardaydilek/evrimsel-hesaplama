"""Dev/demo server entrypoint: `uvicorn arena_core.app:build_app --factory`.

Composes the FastAPI app with a SQLite session factory and an in-process THREADED
enqueue (each submission runs on a background daemon thread via run_submission_job,
so POST returns immediately and the client polls). DEV/DEMO ONLY — production uses
RQ + Redis (see worker.py / M6). The runner is auto-selected by worker._build_runner
(ContainerRunner when Docker is present, else LocalRunner; ARENA_RUNNER=local forces
the stand-in for fast python-only UI iteration).

Factory mode (`--factory`) avoids import-time side effects and keeps build_app()
testable: tests can pass a synchronous enqueue for determinism.
"""
from __future__ import annotations

import os
import threading
from typing import Callable

# The API's session factory AND run_submission_job's own make_engine() must resolve to
# the SAME database, or the background job won't find the just-inserted submission.
# Setting DATABASE_URL once (before make_engine) guarantees they share one SQLite file.
os.environ.setdefault("DATABASE_URL", "sqlite:///./arena_dev.db")

from .api import create_app
from .db import init_db, make_engine, make_session_factory
from .worker import run_submission_job


def _threaded_enqueue(submission_id: str) -> None:
    threading.Thread(target=run_submission_job, args=(submission_id,), daemon=True).start()


def build_app(enqueue: Callable[[int], None] | None = None):
    """Build the dev FastAPI app. `enqueue` defaults to the threaded runner; tests may
    inject a synchronous enqueue for determinism."""
    engine = make_engine()            # reads DATABASE_URL
    init_db(engine)
    session_factory = make_session_factory(engine)
    return create_app(session_factory=session_factory,
                      enqueue=enqueue or _threaded_enqueue)
