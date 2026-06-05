import subprocess

from arena_core.docker_cli import SubprocessDockerCli, DockerOutcome, docker_available


def test_docker_available_true(monkeypatch):
    monkeypatch.setattr("arena_core.docker_cli.which", lambda name: "/usr/local/bin/docker")
    assert docker_available() is True


def test_docker_available_false(monkeypatch):
    monkeypatch.setattr("arena_core.docker_cli.which", lambda name: None)
    assert docker_available() is False


def test_run_maps_completed_process(monkeypatch):
    captured = {}

    class P:
        stdout, stderr, returncode = "out", "err", 0

    def fake_run(argv, **kw):
        captured["argv"] = argv
        captured["kw"] = kw
        return P()

    monkeypatch.setattr(subprocess, "run", fake_run)
    out = SubprocessDockerCli().run(["run", "--rm", "img"], timeout_s=5, stdin="hi")
    assert out.stdout == "out"
    assert out.stderr == "err"
    assert out.exit_code == 0
    assert out.timed_out is False
    assert out.duration_ms >= 0
    assert captured["argv"][0] == "docker"
    assert captured["argv"][1:] == ["run", "--rm", "img"]
    assert captured["kw"]["input"] == "hi"


def test_run_timeout_kills_named(monkeypatch):
    calls = []

    def fake_run(argv, **kw):
        calls.append(argv)
        if argv[:2] == ["docker", "kill"]:
            class K:
                stdout = stderr = ""
                returncode = 0
            return K()
        raise subprocess.TimeoutExpired(cmd=argv, timeout=kw.get("timeout"))

    monkeypatch.setattr(subprocess, "run", fake_run)
    out = SubprocessDockerCli().run(["run", "--name", "c1", "img"], timeout_s=1, kill_name="c1")
    assert out.timed_out is True
    assert out.exit_code is None
    assert ["docker", "kill", "c1"] in calls
