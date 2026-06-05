import json

import fakeredis
import pytest
from rq import Queue, SimpleWorker

from arena_core.db import make_engine, make_session_factory, init_db
from arena_core.models import Submission
from arena_core.local_runner import LocalRunner
from arena_core import worker

OPTIMAL_SOLVER = "print('TOUR ' + ' '.join(str(c) for c in range(1, 43)))"


class InProcessWorker(SimpleWorker):
    """SimpleWorker runs jobs in-process (no fork). RQ 2.9 startup asks Redis for its
    own IP, and fakeredis returns CLIENT LIST without 'addr' (KeyError) — monitoring
    metadata only, so we stub it; the queue/job path is exercised unchanged.
    """

    def _set_ip_address(self, connection):
        self.ip_address = "127.0.0.1"


def _insert_queued(tmp_path, src):
    engine = make_engine(f"sqlite:///{tmp_path}/arena.db")
    init_db(engine)
    sf = make_session_factory(engine)
    with sf() as s:
        sub = Submission(handle="ada", preset="python",
                         files=json.dumps({"main.py": src}), status="queued")
        s.add(sub)
        s.commit()
        return sf, sub.id


def test_enqueued_job_scores_submission(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/arena.db")
    monkeypatch.setattr(worker, "_build_runner", lambda: LocalRunner())
    sf, sid = _insert_queued(tmp_path, OPTIMAL_SOLVER)

    conn = fakeredis.FakeStrictRedis()
    queue = Queue(worker.QUEUE_NAME, connection=conn)
    queue.enqueue(worker.run_submission_job, sid)
    InProcessWorker([queue], connection=conn).work(burst=True)

    with sf() as s:
        sub = s.get(Submission, sid)
        assert sub.status == "scored"
        assert sub.result.length == 699


def test_unexpected_runner_error_marks_failed(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/arena.db")

    class Boom:
        def run(self, spec):
            raise RuntimeError("kaboom")

    monkeypatch.setattr(worker, "_build_runner", lambda: Boom())
    sf, sid = _insert_queued(tmp_path, "print('x')")

    with pytest.raises(RuntimeError):
        worker.run_submission_job(sid)

    with sf() as s:
        sub = s.get(Submission, sid)
        assert sub.status == "failed"
        assert "internal worker error" in sub.fail_reason


def test_build_runner_selects_container_when_docker_present(monkeypatch):
    import arena_core.docker_cli as dc
    from arena_core.container_runner import ContainerRunner
    monkeypatch.setattr(dc, "docker_available", lambda: True)
    monkeypatch.delenv("ARENA_RUNNER", raising=False)
    assert isinstance(worker._build_runner(), ContainerRunner)


def test_build_runner_falls_back_to_local_without_docker(monkeypatch):
    import arena_core.docker_cli as dc
    monkeypatch.setattr(dc, "docker_available", lambda: False)
    monkeypatch.delenv("ARENA_RUNNER", raising=False)
    assert isinstance(worker._build_runner(), LocalRunner)


def test_build_runner_forced_local_by_env(monkeypatch):
    monkeypatch.setenv("ARENA_RUNNER", "local")
    assert isinstance(worker._build_runner(), LocalRunner)
