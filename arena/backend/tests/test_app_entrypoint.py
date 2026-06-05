from fastapi.testclient import TestClient

OPTIMAL = "print('TOUR ' + ' '.join(str(c) for c in range(1, 43)))"


def test_dev_entrypoint_composes_and_scores(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/arena_dev.db")
    monkeypatch.setenv("ARENA_RUNNER", "local")
    from arena_core.app import build_app
    from arena_core.worker import run_submission_job

    app = build_app(enqueue=run_submission_job)   # synchronous: run inline, deterministic
    client = TestClient(app)

    resp = client.post("/api/submissions",
                       json={"handle": "dev", "preset": "python", "files": {"main.py": OPTIMAL}})
    assert resp.status_code == 200
    sid = resp.json()["id"]

    body = client.get(f"/api/submissions/{sid}").json()
    assert body["status"] == "scored"
    assert body["length"] == 699


def test_build_app_default_is_a_fastapi_app(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/arena_dev.db")
    from arena_core.app import build_app
    from fastapi import FastAPI
    app = build_app()   # default (threaded) enqueue; just verify composition
    assert isinstance(app, FastAPI)
