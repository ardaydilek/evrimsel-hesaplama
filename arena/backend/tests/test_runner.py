from arena_core.runner import Runner, RunResult
from arena_core.run_spec import RunSpec


def test_runresult_fields():
    r = RunResult(status="ok", stdout="TOUR 1 2 3", stderr="", exit_code=0, time_ms=12)
    assert r.status == "ok"
    assert r.stdout == "TOUR 1 2 3"
    assert r.exit_code == 0
    assert r.time_ms == 12


def test_runner_protocol_is_structural():
    class Dummy:
        def run(self, spec):
            return RunResult("ok", "", "", 0, 0)

    class NotARunner:
        pass

    assert isinstance(Dummy(), Runner)
    assert not isinstance(NotARunner(), Runner)
    assert Dummy().run(RunSpec(preset="python")).status == "ok"
