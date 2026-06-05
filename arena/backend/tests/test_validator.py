from arena_core.validator import is_valid_tour


def test_valid_permutation():
    ok, reason = is_valid_tour([3, 1, 4, 2], 4)
    assert ok and reason == ""


def test_none_tour():
    ok, reason = is_valid_tour(None, 4)
    assert not ok and "no tour" in reason.lower()


def test_wrong_count():
    ok, reason = is_valid_tour([1, 2, 3], 4)
    assert not ok and "expected 4" in reason


def test_duplicate_city():
    ok, reason = is_valid_tour([1, 2, 2, 4], 4)
    assert not ok and "permutation" in reason.lower()


def test_out_of_range_city():
    ok, reason = is_valid_tour([1, 2, 3, 5], 4)
    assert not ok and "permutation" in reason.lower()
