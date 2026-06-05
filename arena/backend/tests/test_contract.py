from arena_core.contract import parse_stdout


def test_parses_well_formed_output():
    text = "TOUR 1 2 3 4\nLENGTH 13\nGEN 0 100 200\nGEN 1 90 180\n"
    r = parse_stdout(text)
    assert r.tour == [1, 2, 3, 4]
    assert r.claimed_length == 13.0
    assert r.gen_log == [(0, 100.0, 200.0), (1, 90.0, 180.0)]


def test_ignores_noise_lines():
    text = "starting solver...\nTOUR 3 1 2\ndebug: whatever\n"
    r = parse_stdout(text)
    assert r.tour == [3, 1, 2]
    assert r.claimed_length is None
    assert r.gen_log == []


def test_missing_tour_gives_none():
    r = parse_stdout("LENGTH 42\n")
    assert r.tour is None


def test_malformed_recognized_line_is_ignored():
    # a TOUR line with a non-integer token is dropped, not crashed
    r = parse_stdout("TOUR 1 two 3\n")
    assert r.tour is None
