# tests/integration/test_build_proxy.py
import subprocess

import pytest

from arena_core.build_network import build_network

pytestmark = pytest.mark.docker


def _curl(net, env, url):
    args = ["docker", "run", "--rm", "--network", net]
    for key, value in env.items():
        args += ["-e", f"{key}={value}"]
    args += ["curlimages/curl:8.7.1", "-sS", "-f", "-m", "25", "-o", "/dev/null", url]
    return subprocess.run(args, capture_output=True, text=True)


def test_proxy_allows_registry_denies_other():
    with build_network() as (net, env):
        # Probe a small per-package index, NOT /simple/ (the full PyPI index is ~40MB and
        # grows over time — downloading it all would time out and flake). A single package
        # index proves the proxy permits pypi.org just as well, in a few hundred KB.
        allowed = _curl(net, env, "https://pypi.org/simple/pip/")
        denied = _curl(net, env, "https://example.com/")
    assert allowed.returncode == 0, allowed.stderr     # PyPI is on the allowlist
    assert denied.returncode != 0                       # example.com is refused by squid
