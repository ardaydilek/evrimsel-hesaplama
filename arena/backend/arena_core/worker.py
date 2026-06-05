"""Production queue wiring.

The API enqueues `run_submission_job(submission_id)` onto an RQ queue; an RQ worker
process runs it. The job builds a DB session from DATABASE_URL and a Runner, then
delegates to the same `process_submission` pipeline used everywhere.

By default `_build_runner` returns a ContainerRunner when Docker is available (the
production engine) and falls back to the LocalRunner stand-in otherwise. Set
ARENA_RUNNER=local to force the stand-in (used by dev/tests).
"""
from __future__ import annotations

import os

from redis import Redis
from rq import Queue

from . import problem
from .db import init_db, make_engine, make_session_factory
from .local_runner import LocalRunner
from .models import Submission
from .runner import Runner
from .service import process_submission

QUEUE_NAME = "submissions"


def make_redis() -> Redis:
    return Redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))


def make_queue(connection: Redis | None = None) -> Queue:
    return Queue(QUEUE_NAME, connection=connection or make_redis())


def make_enqueue(queue: Queue):
    """Return an enqueue(submission_id) callable that pushes the job onto the queue."""
    def enqueue(submission_id: str) -> None:
        queue.enqueue(run_submission_job, submission_id)
    return enqueue


def _build_runner() -> Runner:
    if os.environ.get("ARENA_RUNNER", "").lower() == "local":
        return LocalRunner()
    from .docker_cli import docker_available
    if docker_available():
        from .container_runner import ContainerRunner
        return ContainerRunner()
    return LocalRunner()


def run_submission_job(submission_id: str) -> None:
    engine = make_engine()
    init_db(engine)
    session_factory = make_session_factory(engine)
    matrix = problem.load_distance_matrix()
    try:
        process_submission(submission_id, session_factory=session_factory,
                           runner=_build_runner(), matrix=matrix)
    except Exception as exc:
        # Safety net: never leave a submission stranded in "running".
        with session_factory() as session:
            sub = session.get(Submission, submission_id)
            if sub is not None and sub.status not in ("scored", "failed"):
                sub.status = "failed"
                sub.fail_reason = f"internal worker error: {type(exc).__name__}"
                session.commit()
        raise
