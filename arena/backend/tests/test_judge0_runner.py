from arena_core.judge0_runner import Judge0Runner

LANGS = {"python": 71, "cpp": 54}


class FakeClient:
    """Stand-in for the HTTP client: records the create payload, returns a fixed result."""
    def __init__(self, result):
        self.result = result
        self.created = None

    def create_submission(self, payload):
        self.created = payload
        return "tok-1"

    def get_submission(self, token):
        return self.result


class SequenceClient:
    """Returns a sequence of results across polls (to exercise the polling loop)."""
    def __init__(self, results):
        self.results = list(results)
        self.created = None

    def create_submission(self, payload):
        self.created = payload
        return "tok-1"

    def get_submission(self, token):
        return self.results.pop(0)


def test_builds_submission_request():
    fake = FakeClient({"status": {"id": 3}, "stdout": "TOUR 1 2 3", "time": "0.012"})
    Judge0Runner(fake, LANGS).run("python", "print('x')", stdin="data")
    assert fake.created["language_id"] == 71
    assert fake.created["source_code"] == "print('x')"
    assert fake.created["stdin"] == "data"


def test_accepted_maps_to_ok():
    fake = FakeClient({"status": {"id": 3}, "stdout": "TOUR 1 2 3", "time": "0.012"})
    r = Judge0Runner(fake, LANGS).run("python", "x")
    assert r.status == "ok"
    assert "TOUR 1 2 3" in r.stdout
    assert r.time_ms == 12          # 0.012 s -> 12 ms


def test_time_limit_exceeded_maps_to_timeout():
    fake = FakeClient({"status": {"id": 5}, "stdout": "", "time": "2.0"})
    r = Judge0Runner(fake, LANGS).run("python", "x")
    assert r.status == "timeout"


def test_compile_error_maps_to_error_with_message():
    fake = FakeClient({"status": {"id": 6}, "compile_output": "boom: missing ;", "stdout": ""})
    r = Judge0Runner(fake, LANGS).run("cpp", "x")
    assert r.status == "error"
    assert "boom" in r.stderr


def test_polls_until_terminal():
    seq = SequenceClient([
        {"status": {"id": 2}},                                     # Processing
        {"status": {"id": 3}, "stdout": "TOUR 1", "time": "0.1"},   # Accepted
    ])
    r = Judge0Runner(seq, LANGS, poll_interval_s=0).run("python", "x")
    assert r.status == "ok"
    assert "TOUR 1" in r.stdout


def test_unsupported_language():
    r = Judge0Runner(FakeClient({}), LANGS).run("cobol", "x")
    assert r.status == "error"
    assert "unsupported" in r.stderr.lower()


def test_missing_time_is_zero():
    fake = FakeClient({"status": {"id": 3}, "stdout": "TOUR 1"})  # no "time" field
    r = Judge0Runner(fake, LANGS).run("python", "x")
    assert r.status == "ok"
    assert r.time_ms == 0


def test_runtime_error_keeps_existing_stderr():
    # status 7 (runtime error) with BOTH stderr and compile_output: stderr must win
    fake = FakeClient({"status": {"id": 7}, "stderr": "real stderr", "compile_output": "cmp"})
    r = Judge0Runner(fake, LANGS).run("python", "x")
    assert r.status == "error"
    assert r.stderr == "real stderr"
