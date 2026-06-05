import json

from arena_core.db import make_engine, make_session_factory, init_db
from arena_core.models import Submission
from arena_core.local_runner import LocalRunner
from arena_core.service import process_submission
from arena_core import problem

OPTIMAL_SOLVER = "print('TOUR ' + ' '.join(str(c) for c in range(1, 43)))"   # identity tour -> 699
BAD_TOUR_SOLVER = "print('TOUR 1 2 3')"                                       # too short
CRASH_SOLVER = "raise SystemExit(1)"


def _setup(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path}/arena.db")
    init_db(engine)
    sf = make_session_factory(engine)
    return sf, problem.load_distance_matrix()


def _submit(sf, src):
    with sf() as s:
        sub = Submission(handle="t", preset="python",
                         files=json.dumps({"main.py": src}), status="queued")
        s.add(sub)
        s.commit()
        return sub.id


def test_valid_submission_is_scored(tmp_path):
    sf, matrix = _setup(tmp_path)
    sid = _submit(sf, OPTIMAL_SOLVER)
    process_submission(sid, session_factory=sf, runner=LocalRunner(), matrix=matrix)
    with sf() as s:
        sub = s.get(Submission, sid)
        assert sub.status == "scored"
        assert sub.result.length == 699
        assert json.loads(sub.result.tour) == list(range(1, 43))


def test_illegal_tour_fails_with_reason(tmp_path):
    sf, matrix = _setup(tmp_path)
    sid = _submit(sf, BAD_TOUR_SOLVER)
    process_submission(sid, session_factory=sf, runner=LocalRunner(), matrix=matrix)
    with sf() as s:
        sub = s.get(Submission, sid)
        assert sub.status == "failed"
        assert "expected 42" in sub.fail_reason
        assert sub.result is None


def test_crashing_submission_fails(tmp_path):
    sf, matrix = _setup(tmp_path)
    sid = _submit(sf, CRASH_SOLVER)
    process_submission(sid, session_factory=sf, runner=LocalRunner(), matrix=matrix)
    with sf() as s:
        sub = s.get(Submission, sid)
        assert sub.status == "failed"
        assert sub.fail_reason
