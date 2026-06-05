from arena_core import build_network as bn


def test_build_network_provisions_and_tears_down(monkeypatch):
    created, removed = [], []

    def fake_run(cmd):                 # the check=True provisioning helper
        created.append(cmd)
        return ""

    class Done:
        returncode = 0
        stdout = stderr = ""

    def fake_subprocess_run(cmd, **kw):   # teardown (best-effort, no check)
        removed.append(cmd)
        return Done()

    monkeypatch.setattr(bn, "_run", fake_run)
    monkeypatch.setattr(bn.subprocess, "run", fake_subprocess_run)

    with bn.build_network() as (net, env):
        assert net.startswith("arena-build-int-")
        assert env["HTTPS_PROXY"].startswith("http://arena-proxy-")
        assert env["HTTPS_PROXY"].endswith(":3128")
        assert env["HTTP_PROXY"] == env["HTTPS_PROXY"]

    joined = [" ".join(c) for c in created]
    assert any("network create --internal" in j for j in joined)
    assert any(c[:3] == ["docker", "run", "-d"] for c in created)
    assert any("network connect" in j for j in joined)

    joined_rm = [" ".join(c) for c in removed]
    assert any("rm -f arena-proxy-" in j for j in joined_rm)
    assert sum("network rm" in j for j in joined_rm) == 2
