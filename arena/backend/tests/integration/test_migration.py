"""Gated: apply Alembic migrations to a real throwaway Postgres and assert the schema.
Requires Docker (conftest auto-skips when absent) and psycopg in the venv."""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path

import pytest

pytestmark = pytest.mark.docker

BACKEND = Path(__file__).resolve().parents[2]   # arena/backend


def _free_port() -> str:
    """Grab an ephemeral free port on loopback (avoids a hardcoded-port collision)."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return str(s.getsockname()[1])


def _pg_ready(url: str, deadline: float) -> bool:
    from sqlalchemy import create_engine
    engine = create_engine(url)
    try:
        while time.time() < deadline:
            try:
                engine.connect().close()
                return True
            except Exception:
                time.sleep(1)
        return False
    finally:
        engine.dispose()


def test_alembic_upgrade_head_creates_schema():
    from sqlalchemy import create_engine, inspect

    name = "arena-pg-" + uuid.uuid4().hex[:8]
    port = _free_port()
    url = f"postgresql+psycopg://t:t@127.0.0.1:{port}/t"
    subprocess.run(
        ["docker", "run", "-d", "--rm", "--name", name,
         "-e", "POSTGRES_USER=t", "-e", "POSTGRES_PASSWORD=t", "-e", "POSTGRES_DB=t",
         "-p", f"127.0.0.1:{port}:5432", "postgres:16"],
        check=True, capture_output=True)
    engine = None
    try:
        assert _pg_ready(url, time.time() + 60), "postgres did not become ready"
        env = {**os.environ, "DATABASE_URL": url}
        res = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"],
                             cwd=str(BACKEND), env=env, capture_output=True, text=True)
        assert res.returncode == 0, res.stderr

        engine = create_engine(url)
        insp = inspect(engine)
        tables = set(insp.get_table_names())
        assert {"submissions", "results"} <= tables
        sub_cols = {c["name"] for c in insp.get_columns("submissions")}
        assert {"id", "handle", "preset", "status", "created_at"} <= sub_cols
        # The FK is the main cross-table surface that naming-convention / autogenerate
        # bugs tend to break, so assert it landed.
        assert insp.get_foreign_keys("results"), "results.submission_id FK missing"
        # And that the upgrade actually reached head (the one migration is stamped).
        with engine.connect() as conn:
            version = conn.exec_driver_sql("SELECT version_num FROM alembic_version").scalar()
        assert version == "0001_initial"
    finally:
        if engine is not None:
            engine.dispose()
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)
