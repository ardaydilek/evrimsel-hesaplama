from fastapi.testclient import TestClient

from arena_core.db import make_engine, make_session_factory, init_db
from arena_core.local_runner import LocalRunner
from arena_core.service import process_submission
from arena_core.api import create_app
from arena_core import problem

OPTIMAL_SOLVER = "print('TOUR ' + ' '.join(str(c) for c in range(1, 43)))"


def _client(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path}/arena.db")
    init_db(engine)
    sf = make_session_factory(engine)
    matrix = problem.load_distance_matrix()
    coords = problem.load_coordinates()

    def enqueue(submission_id):   # synchronous inline dispatch for tests
        process_submission(submission_id, session_factory=sf, runner=LocalRunner(), matrix=matrix)

    return TestClient(create_app(session_factory=sf, enqueue=enqueue, matrix=matrix, coords=coords))


def _submit(client, **over):
    body = {"handle": "ada", "preset": "python", "files": {"main.py": OPTIMAL_SOLVER}}
    body.update(over)
    return client.post("/api/submissions", json=body)


def test_submit_then_status_is_scored(tmp_path):
    client = _client(tmp_path)
    resp = _submit(client)
    assert resp.status_code == 200
    sub_id = resp.json()["id"]
    assert sub_id.startswith("ada-")  # handle-derived, slug + random

    body = client.get(f"/api/submissions/{sub_id}").json()
    assert body["status"] == "scored"
    assert body["preset"] == "python"
    assert body["length"] == 699
    assert body["tour"] == list(range(1, 43))
    assert body["gen_log"] is None


def test_leaderboard_lists_scored(tmp_path):
    client = _client(tmp_path)
    _submit(client)
    board = client.get("/api/leaderboard").json()
    assert len(board) == 1
    assert board[0]["handle"] == "ada"
    assert board[0]["preset"] == "python"
    assert board[0]["length"] == 699
    assert board[0]["gap"] == 0


def test_unknown_preset_is_422(tmp_path):
    client = _client(tmp_path)
    assert _submit(client, preset="brainfuck").status_code == 422


def test_empty_files_is_422(tmp_path):
    client = _client(tmp_path)
    assert _submit(client, files={}).status_code == 422


def test_path_traversal_is_422(tmp_path):
    client = _client(tmp_path)
    assert _submit(client, files={"../evil.py": "x"}).status_code == 422


def test_problem_endpoint(tmp_path):
    client = _client(tmp_path)
    body = client.get("/api/problem").json()
    assert body["num_cities"] == 42
    assert body["optimal"] == 699
    assert len(body["matrix"]) == 42
    assert len(body["coordinates"]) == 42


def test_missing_submission_404(tmp_path):
    client = _client(tmp_path)
    assert client.get("/api/submissions/99999").status_code == 404


def test_presets_endpoint(tmp_path):
    client = _client(tmp_path)
    body = client.get("/api/presets").json()
    names = [p["name"] for p in body]
    assert set(names) == {"python", "cpp", "go", "rust", "node", "java"}
    cpp = next(p for p in body if p["name"] == "cpp")
    assert cpp["default_build_cmd"] == "make"
    assert cpp["default_run_cmd"] == "./solver"
    py = next(p for p in body if p["name"] == "python")
    assert py["default_build_cmd"] is None
    assert py["default_run_cmd"] == "python3 main.py"
