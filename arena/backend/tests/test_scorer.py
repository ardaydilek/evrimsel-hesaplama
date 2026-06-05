from arena_core import problem
from arena_core.scorer import score_stdout

PHASE1_TOUR_LINE = "TOUR " + " ".join(str(c) for c in [
    32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    25, 26, 27, 24, 11, 12, 13, 14, 15, 16, 18, 19, 20, 17, 23, 22, 21, 28, 29, 30, 31,
])


def test_scores_valid_submission_with_authoritative_length():
    matrix = problem.load_distance_matrix()
    text = PHASE1_TOUR_LINE + "\nLENGTH 999\nGEN 0 2393 2501\n"  # claim is wrong on purpose
    r = score_stdout(text, matrix)
    assert r.valid is True
    assert r.length == 709                 # recomputed, NOT the claimed 999
    assert r.claimed_length == 999.0
    assert r.gen_log == [(0, 2393.0, 2501.0)]


def test_rejects_illegal_tour():
    matrix = problem.load_distance_matrix()
    r = score_stdout("TOUR 1 2 3\n", matrix)   # too short
    assert r.valid is False
    assert r.length is None
    assert "expected 42" in r.reason


def test_rejects_missing_tour():
    matrix = problem.load_distance_matrix()
    r = score_stdout("no result here\n", matrix)
    assert r.valid is False
    assert "no tour" in r.reason.lower()
