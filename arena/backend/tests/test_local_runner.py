from arena_core.local_runner import LocalRunner
from arena_core.run_spec import RunSpec


def _py(src):
    return RunSpec(preset="python", files={"main.py": src})


def test_runs_python_and_captures_stdout():
    r = LocalRunner().run(_py("print('TOUR 1 2 3')"))
    assert r.status == "ok"
    assert "TOUR 1 2 3" in r.stdout
    assert r.exit_code == 0
    assert r.time_ms >= 0


def test_reads_stdin():
    r = LocalRunner().run(RunSpec(preset="python",
                                  files={"main.py": "import sys\nprint('GOT', sys.stdin.read().strip())"},
                                  stdin="hello"))
    assert r.status == "ok"
    assert "GOT hello" in r.stdout


def test_timeout():
    r = LocalRunner(timeout_s=0.3).run(_py("while True:\n    pass"))
    assert r.status == "timeout"
    assert r.exit_code is None


def test_runtime_error_is_error_status():
    r = LocalRunner().run(_py("raise SystemExit(3)"))
    assert r.status == "error"
    assert r.exit_code == 3


def test_unsafe_path_is_error():
    r = LocalRunner().run(RunSpec(preset="python", files={"../evil.py": "x"}))
    assert r.status == "error"
    assert "traversal" in r.stderr.lower()
