"""FastAPI application factory.

Dependencies (session factory, enqueue callable, problem data) are injected, so the
app is fully testable with SQLite + an inline enqueue + LocalRunner. In production the
same factory is wired with a Postgres session factory and an RQ-backed enqueue.
"""
from __future__ import annotations

import json
from typing import Callable

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from . import problem
from .models import Result, Submission
from .presets import PRESETS
from .workdir import check_files


class SubmissionIn(BaseModel):
    handle: str
    preset: str
    files: dict[str, str]
    build_cmd: str | None = None
    run_cmd: str | None = None


def create_app(*, session_factory, enqueue: Callable[[str], None],
               matrix=None, coords=None) -> FastAPI:
    matrix = matrix if matrix is not None else problem.load_distance_matrix()
    coords = coords if coords is not None else problem.load_coordinates()

    app = FastAPI(title="TSP Solver Arena")

    @app.post("/api/submissions")
    def submit(body: SubmissionIn):
        if body.preset not in PRESETS:
            raise HTTPException(status_code=422, detail=f"unknown preset: {body.preset}")
        try:
            check_files(body.files)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))

        files_json = json.dumps(body.files)
        with session_factory() as session:
            for _ in range(5):
                sub = Submission(handle=body.handle,
                                 preset=body.preset, files=files_json,
                                 build_cmd=body.build_cmd, run_cmd=body.run_cmd,
                                 status="queued")
                session.add(sub)
                try:
                    session.commit()
                    break
                except IntegrityError:
                    session.rollback()  # id collision — regenerate and retry
            else:
                raise HTTPException(status_code=500, detail="could not allocate submission id")
            sub_id = sub.id
        enqueue(sub_id)
        return {"id": sub_id, "status": "queued"}

    @app.get("/api/submissions/{submission_id}")
    def get_submission(submission_id: str):
        with session_factory() as session:
            sub = session.get(Submission, submission_id)
            if sub is None:
                raise HTTPException(status_code=404, detail="submission not found")
            body = {
                "id": sub.id, "handle": sub.handle, "preset": sub.preset,
                "status": sub.status, "fail_reason": sub.fail_reason,
            }
            if sub.result is not None:
                body["length"] = sub.result.length
                body["runtime_ms"] = sub.result.runtime_ms
                body["tour"] = json.loads(sub.result.tour)
                body["gen_log"] = json.loads(sub.result.gen_log) if sub.result.gen_log else None
            return body

    @app.get("/api/leaderboard")
    def leaderboard():
        with session_factory() as session:
            rows = session.execute(
                select(Submission, Result)
                .join(Result, Result.submission_id == Submission.id)
                .where(Submission.status == "scored")
                .order_by(Result.length.asc(), Result.runtime_ms.asc())
            ).all()
            return [
                {"id": s.id, "handle": s.handle, "preset": s.preset,
                 "length": r.length, "gap": r.length - problem.OPTIMAL_LENGTH,
                 "runtime_ms": r.runtime_ms}
                for s, r in rows
            ]

    @app.get("/api/problem")
    def get_problem():
        return {
            "num_cities": problem.NUM_CITIES,
            "optimal": problem.OPTIMAL_LENGTH,
            "matrix": matrix,
            "coordinates": coords,
        }

    @app.get("/api/presets")
    def list_presets():
        return [
            {"name": p.name,
             "default_build_cmd": p.default_build_cmd,
             "default_run_cmd": p.default_run_cmd}
            for p in PRESETS.values()
        ]

    return app
