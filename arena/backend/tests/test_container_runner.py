from arena_core.container_runner import ContainerRunner
from arena_core.docker_cli import DockerOutcome
from arena_core.run_spec import RunSpec, ResourceLimits


class FakeDocker:
    """Records each run() argv and returns scripted outcomes in order."""
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def run(self, args, *, timeout_s, stdin="", kill_name=None):
        self.calls.append(args)
        return self.outcomes.pop(0)


def _ok(stdout="TOUR 1 2 3", code=0):
    return DockerOutcome(stdout, "", code, False, 5)


def _net_value(args):
    return args[args.index("--network") + 1]


def test_python_runs_single_phase_network_none():
    fake = FakeDocker([_ok("TOUR 1 2 3")])
    r = ContainerRunner(docker=fake).run(
        RunSpec(preset="python", files={"main.py": "print('TOUR 1 2 3')"}))
    assert r.status == "ok"
    assert "TOUR 1 2 3" in r.stdout
    assert len(fake.calls) == 1                 # python has no build phase
    args = fake.calls[0]
    assert _net_value(args) == "none"
    assert "512m" in args                       # run memory cap
    assert "--read-only" in args
    assert "--user" in args                     # run phase drops privileges
    assert args[-3:] == ["sh", "-c", "python3 main.py"]


def test_run_timeout_maps_to_timeout():
    fake = FakeDocker([DockerOutcome("", "", None, True, 10000)])
    r = ContainerRunner(docker=fake).run(RunSpec(preset="python", files={"main.py": "x"}))
    assert r.status == "timeout"
    assert r.exit_code is None


def test_run_nonzero_exit_maps_to_error():
    fake = FakeDocker([_ok("", code=1)])
    r = ContainerRunner(docker=fake).run(RunSpec(preset="python", files={"main.py": "x"}))
    assert r.status == "error"


def test_output_is_truncated():
    fake = FakeDocker([_ok("A" * 2_000_000)])
    r = ContainerRunner(docker=fake,
                        run_limits=ResourceLimits(512, 1.0, 10, 128, 1000)
                        ).run(RunSpec(preset="python", files={"main.py": "x"}))
    assert len(r.stdout) == 1000


def test_output_truncated_by_bytes_not_chars():
    # 2000 multibyte chars (2 bytes each in UTF-8) with a 100-byte cap -> <=100 bytes, valid UTF-8
    fake = FakeDocker([_ok("é" * 2000)])   # é = 2 bytes in UTF-8
    r = ContainerRunner(docker=fake,
                        run_limits=ResourceLimits(512, 1.0, 10, 128, 100)
                        ).run(RunSpec(preset="python", files={"main.py": "x"}))
    assert len(r.stdout.encode("utf-8")) <= 100
    assert "é" not in r.stdout or r.stdout == "é" * 50  # clean decode, no partial char


def test_unsafe_path_errors_before_docker():
    fake = FakeDocker([])
    r = ContainerRunner(docker=fake).run(RunSpec(preset="python", files={"../evil.py": "x"}))
    assert r.status == "error"
    assert "traversal" in r.stderr.lower()
    assert len(fake.calls) == 0


def test_unknown_preset_errors_before_docker():
    fake = FakeDocker([])
    r = ContainerRunner(docker=fake).run(RunSpec(preset="cobol", files={"a.cob": "x"}))
    assert r.status == "error"
    assert "unknown preset" in r.stderr
    assert len(fake.calls) == 0


def test_run_phase_mounts_work_readonly():
    fake = FakeDocker([_ok()])
    ContainerRunner(docker=fake).run(RunSpec(preset="python", files={"main.py": "x"}))
    args = fake.calls[0]
    vol = args[args.index("--volume") + 1]
    assert vol.endswith(":/work:ro")           # run phase must mount /work read-only


def test_run_phase_tmpfs_is_noexec():
    fake = FakeDocker([_ok()])
    ContainerRunner(docker=fake).run(RunSpec(preset="python", files={"main.py": "x"}))
    args = fake.calls[0]
    tmpfs = args[args.index("--tmpfs") + 1]
    assert "noexec" in tmpfs and "exec," not in tmpfs   # untrusted /tmp must be noexec


def test_interactive_only_when_stdin():
    fake_no = FakeDocker([_ok()])
    ContainerRunner(docker=fake_no).run(RunSpec(preset="python", files={"main.py": "x"}))
    assert "--interactive" not in fake_no.calls[0]

    fake_yes = FakeDocker([_ok()])
    ContainerRunner(docker=fake_yes).run(RunSpec(preset="python", files={"main.py": "x"}, stdin="data"))
    assert "--interactive" in fake_yes.calls[0]


def test_run_phase_pins_hardening_flags():
    fake = FakeDocker([_ok()])
    ContainerRunner(docker=fake).run(RunSpec(preset="python", files={"main.py": "x"}))
    args = fake.calls[0]
    joined = " ".join(args)
    assert "--cap-drop ALL" in joined
    assert "--security-opt no-new-privileges" in joined
    assert "--memory-swap 512m" in joined         # swap disabled (== memory)
    assert "--pids-limit 128" in joined
    assert "--ulimit nofile=4096:4096" in joined
    assert "--cgroupns private" in joined
    assert "--network none" in joined


def test_cpp_runs_build_then_run():
    fake = FakeDocker([_ok("", code=0), _ok("TOUR 1 2 3")])   # build ok, then run ok
    r = ContainerRunner(docker=fake).run(
        RunSpec(preset="cpp",
                files={"main.cpp": "x", "Makefile": "all:\n\tg++ main.cpp -o solver"}))
    assert r.status == "ok"
    assert "TOUR 1 2 3" in r.stdout
    assert len(fake.calls) == 2
    build_args, run_args = fake.calls
    assert build_args[-3:] == ["sh", "-c", "make"]
    assert _net_value(build_args) == "none"          # cpp build needs no network
    assert "1024m" in build_args                      # build memory cap
    assert "--user" not in build_args                 # build keeps image-default user
    assert run_args[-3:] == ["sh", "-c", "./solver"]


def test_build_failure_short_circuits():
    fake = FakeDocker([_ok("error: missing ;", code=1)])   # build fails; run never happens
    r = ContainerRunner(docker=fake).run(RunSpec(preset="cpp", files={"main.cpp": "x"}))
    assert r.status == "error"
    assert "missing ;" in r.stderr
    assert len(fake.calls) == 1


def test_networked_build_uses_provider_network_and_proxy_env():
    from contextlib import contextmanager

    @contextmanager
    def provider():
        yield ("arena-build-net", {"HTTPS_PROXY": "http://proxy:3128"})

    fake = FakeDocker([_ok("", code=0), _ok("TOUR 1 2 3")])
    r = ContainerRunner(docker=fake, build_network_provider=provider).run(
        RunSpec(preset="go", files={"main.go": "package main", "go.mod": "module m"}))
    assert r.status == "ok"
    build_args = fake.calls[0]
    assert _net_value(build_args) == "arena-build-net"
    assert "HTTPS_PROXY=http://proxy:3128" in build_args


def test_build_phase_tmpfs_is_exec():
    # build toolchains may exec helper scripts from /tmp, so the build phase opts into exec
    fake = FakeDocker([_ok("", code=0), _ok("TOUR 1 2 3")])
    ContainerRunner(docker=fake).run(RunSpec(preset="cpp", files={"main.cpp": "x"}))
    build_args = fake.calls[0]
    tmpfs = build_args[build_args.index("--tmpfs") + 1]
    assert tmpfs.endswith(",exec")


def test_build_tmpfs_is_large_and_exec():
    fake = FakeDocker([_ok("", code=0), _ok("TOUR 1 2 3")])
    ContainerRunner(docker=fake).run(RunSpec(preset="cpp", files={"main.cpp": "x"}))
    build_args = fake.calls[0]
    tmpfs = build_args[build_args.index("--tmpfs") + 1]
    assert "size=512m" in tmpfs
    assert tmpfs.endswith(",exec")


def test_run_tmpfs_is_small_and_noexec():
    fake = FakeDocker([_ok("TOUR 1 2 3")])
    ContainerRunner(docker=fake).run(RunSpec(preset="python", files={"main.py": "x"}))
    run_args = fake.calls[0]
    tmpfs = run_args[run_args.index("--tmpfs") + 1]
    assert "size=64m" in tmpfs
    assert "noexec" in tmpfs


import tempfile


def _vol_src(args):
    vol = args[args.index("--volume") + 1]
    return vol.split(":/work")[0]


def test_work_dir_param_places_workdir_under_base(tmp_path):
    fake = FakeDocker([_ok()])
    ContainerRunner(docker=fake, work_dir=str(tmp_path)).run(
        RunSpec(preset="python", files={"main.py": "x"}))
    assert _vol_src(fake.calls[0]).startswith(str(tmp_path))


def test_work_dir_falls_back_to_env(monkeypatch, tmp_path):
    monkeypatch.setenv("ARENA_WORK_DIR", str(tmp_path))
    fake = FakeDocker([_ok()])
    ContainerRunner(docker=fake).run(RunSpec(preset="python", files={"main.py": "x"}))
    assert _vol_src(fake.calls[0]).startswith(str(tmp_path))


def test_work_dir_default_uses_system_temp(monkeypatch):
    monkeypatch.delenv("ARENA_WORK_DIR", raising=False)
    fake = FakeDocker([_ok()])
    ContainerRunner(docker=fake).run(RunSpec(preset="python", files={"main.py": "x"}))
    assert _vol_src(fake.calls[0]).startswith(tempfile.gettempdir())


def test_copy_problem_data_provides_files(tmp_path):
    from arena_core.container_runner import copy_problem_data
    copy_problem_data(str(tmp_path), set())
    assert (tmp_path / "cityData.txt").exists()
    assert (tmp_path / "intercityDistance.txt").exists()


def test_copy_problem_data_keeps_uploaded(tmp_path):
    from arena_core.container_runner import copy_problem_data
    (tmp_path / "cityData.txt").write_text("MINE")
    copy_problem_data(str(tmp_path), {"cityData.txt"})
    assert (tmp_path / "cityData.txt").read_text() == "MINE"        # not overwritten
    assert (tmp_path / "intercityDistance.txt").exists()           # the other still provided


import os
import stat


class _StattingDocker:
    """Records the workdir's mode (from the --volume arg) at each docker.run call."""
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.modes = []

    def run(self, args, *, timeout_s, stdin="", kill_name=None):
        work = _vol_src(args)
        self.modes.append(stat.S_IMODE(os.stat(work).st_mode))
        return self.outcomes.pop(0)


def test_build_workdir_is_world_writable(tmp_path):
    # The build phase runs as the image-default user, which under gVisor can't write into
    # the 0755 worker-owned workdir; the linker fails ("cannot open output file solver:
    # Permission denied"). The workdir must be world-writable when the build runs.
    fake = _StattingDocker([_ok("", code=0), _ok("TOUR 1 2 3")])
    r = ContainerRunner(docker=fake, work_dir=str(tmp_path)).run(
        RunSpec(preset="cpp",
                files={"main.cpp": "x", "Makefile": "all:\n\tg++ main.cpp -o solver"}))
    assert r.status == "ok"
    build_mode, _run_mode = fake.modes
    assert build_mode & 0o002, "build workdir must be other-writable for the non-owner build user"


def test_run_only_workdir_is_not_world_writable(tmp_path):
    # No build phase (python) → the workdir is never widened past 0755; the run phase
    # only needs to read/traverse it (it mounts /work read-only anyway).
    fake = _StattingDocker([_ok("TOUR 1 2 3")])
    ContainerRunner(docker=fake, work_dir=str(tmp_path)).run(
        RunSpec(preset="python", files={"main.py": "x"}))
    assert not (fake.modes[0] & 0o002), "run-only workdir should stay 0755 (not world-writable)"
