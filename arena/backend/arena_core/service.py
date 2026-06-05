"""The submission pipeline: run the code (sandboxed via the injected Runner), score
it with the authoritative scorer, and persist the outcome.

Runner and the distance matrix are injected so this is testable with LocalRunner +
SQLite and reusable in production with ContainerRunner + Postgres.
"""
from __future__ import annotations

import json

from .models import Result, Submission
from .run_spec import RunSpec
from .runner import Runner
from .scorer import score_stdout


def process_submission(submission_id: int, *, session_factory, runner: Runner, matrix) -> None:
    with session_factory() as session:
        sub = session.get(Submission, submission_id)
        if sub is None:
            return

        sub.status = "running"
        session.commit()

        spec = RunSpec(
            preset=sub.preset,
            files=json.loads(sub.files),
            build_cmd=sub.build_cmd,
            run_cmd=sub.run_cmd,
            mode=sub.mode,
        )
        run = runner.run(spec)

        if run.status != "ok":
            sub.status = "failed"
            sub.fail_reason = (
                "execution timed out" if run.status == "timeout"
                else (run.stderr.strip()[:500] or "execution error")
            )
            session.commit()
            return

        score = score_stdout(run.stdout, matrix)
        if not score.valid:
            sub.status = "failed"
            sub.fail_reason = score.reason
            session.commit()
            return

        sub.status = "scored"
        sub.result = Result(
            length=score.length,
            runtime_ms=run.time_ms,
            tour=json.dumps(score.tour),
            gen_log=json.dumps(score.gen_log) if score.gen_log else None,
        )
        session.commit()
