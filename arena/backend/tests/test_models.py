import json

from arena_core.db import make_engine, make_session_factory, init_db
from arena_core.models import Submission, Result


def _session_factory(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path}/arena.db")
    init_db(engine)
    return make_session_factory(engine)


def test_create_and_read_submission(tmp_path):
    sf = _session_factory(tmp_path)
    with sf() as s:
        sub = Submission(handle="ada", preset="python",
                         files=json.dumps({"main.py": "print(1)"}), status="queued")
        s.add(sub)
        s.commit()
        sub_id = sub.id

    with sf() as s:
        got = s.get(Submission, sub_id)
        assert got.handle == "ada"
        assert got.preset == "python"
        assert got.mode == "preset"
        assert json.loads(got.files) == {"main.py": "print(1)"}
        assert got.build_cmd is None
        assert got.status == "queued"
        assert got.created_at is not None
        assert got.result is None


def test_submission_with_result(tmp_path):
    sf = _session_factory(tmp_path)
    with sf() as s:
        sub = Submission(handle="ada", preset="cpp",
                         files=json.dumps({"main.cpp": "x"}), build_cmd="make",
                         run_cmd="./solver", status="scored")
        sub.result = Result(length=709, runtime_ms=12, tour="[1, 2, 3]", gen_log=None)
        s.add(sub)
        s.commit()
        sub_id = sub.id

    with sf() as s:
        got = s.get(Submission, sub_id)
        assert got.build_cmd == "make"
        assert got.result.length == 709
        assert got.result.runtime_ms == 12
