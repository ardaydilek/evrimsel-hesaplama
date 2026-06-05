from arena_core import problem

# The Phase 1 C++ solver's known best tour (1-based ids) -> must recompute to 709.
PHASE1_TOUR_709 = [
    32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    25, 26, 27, 24, 11, 12, 13, 14, 15, 16, 18, 19, 20, 17, 23, 22, 21, 28, 29, 30, 31,
]


def test_constants():
    assert problem.NUM_CITIES == 42
    assert problem.OPTIMAL_LENGTH == 699


def test_load_distance_matrix():
    m = problem.load_distance_matrix()
    assert len(m) == 42 and all(len(row) == 42 for row in m)
    assert m[0][0] == 0
    assert m[0][1] == 8          # city 1 -> city 2
    assert m[2][3] == 9 and m[2][3] == m[3][2]   # symmetric


def test_load_coordinates():
    c = problem.load_coordinates()
    assert len(c) == 42
    assert c[0] == (170.0, 85.0)
    assert c[41] == (174.0, 87.0)


def test_tour_length_on_synthetic_matrix():
    # 4-city closed tour 1-2-3-4-(back to 1): 1+1+1+10 = 13
    m = [[0, 1, 10, 10], [1, 0, 1, 10], [10, 1, 0, 1], [10, 10, 1, 0]]
    assert problem.tour_length([1, 2, 3, 4], m) == 13
    assert problem.tour_length([1, 3, 2, 4], m) == 31


def test_tour_length_matches_phase1_reference():
    m = problem.load_distance_matrix()
    assert problem.tour_length(PHASE1_TOUR_709, m) == 709
