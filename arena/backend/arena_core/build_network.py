"""Provision the proxied build network: an --internal Docker network whose only egress
is the domain-allowlist squid proxy (docker/proxy). Build containers join the internal
network and use HTTP(S)_PROXY to reach permitted package registries; everything else is
denied. The proxy is dual-homed (internal network + a normal egress network) so it — and
only it — can reach the internet.

build_network() is a context manager yielding (internal_network_name, proxy_env). On
exit it tears down the proxy container and both networks. Real Docker only; the orchestration
is unit-tested with mocks and the allow/deny behavior is integration-tested (Task 20).
"""
from __future__ import annotations

import subprocess
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager

PROXY_IMAGE = "arena/proxy:1"
PROXY_PORT = 3128
PROXY_READY_TIMEOUT = 30.0   # seconds to wait for squid to start listening
PROXY_READY_INTERVAL = 0.3   # poll cadence


def _run(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()


def _wait_for_proxy(proxy_name: str) -> None:
    """Block until squid inside the proxy container accepts connections on PROXY_PORT.

    `docker run -d` returns as soon as the container is created, not when squid has
    bound its port; handing back proxy_env before that races the first client request
    (curl/pip would get a connection-refused on an allowed host). We probe from inside
    the container using bash's /dev/tcp builtin (the ubuntu/squid image has bash but no
    nc/curl/squidclient) so the check works even though the proxy is on an --internal
    network unreachable from the host. Raises if the proxy never comes up.
    """
    deadline = time.monotonic() + PROXY_READY_TIMEOUT
    probe = ["docker", "exec", proxy_name, "bash", "-c",
             f"(echo > /dev/tcp/127.0.0.1/{PROXY_PORT})"]
    last = None
    while time.monotonic() < deadline:
        last = subprocess.run(probe, capture_output=True, text=True)
        if last.returncode == 0:
            return
        time.sleep(PROXY_READY_INTERVAL)
    detail = (last.stderr or last.stdout or "").strip() if last else ""
    raise RuntimeError(
        f"proxy {proxy_name} did not start listening on :{PROXY_PORT} "
        f"within {PROXY_READY_TIMEOUT:.0f}s{f': {detail}' if detail else ''}"
    )


@contextmanager
def build_network() -> Iterator[tuple[str, dict[str, str]]]:
    token = uuid.uuid4().hex[:10]
    internal_net = f"arena-build-int-{token}"   # --internal: no route to the internet
    egress_net = f"arena-build-eg-{token}"      # the proxy's own path out
    proxy_name = f"arena-proxy-{token}"
    try:
        _run(["docker", "network", "create", "--internal", internal_net])
        _run(["docker", "network", "create", egress_net])
        _run(["docker", "run", "-d", "--name", proxy_name, "--network", internal_net, PROXY_IMAGE])
        _run(["docker", "network", "connect", egress_net, proxy_name])
        _wait_for_proxy(proxy_name)   # don't hand back proxy_env until squid is listening
        proxy_url = f"http://{proxy_name}:{PROXY_PORT}"
        proxy_env = {
            "HTTP_PROXY": proxy_url, "HTTPS_PROXY": proxy_url,
            "http_proxy": proxy_url, "https_proxy": proxy_url,
        }
        yield internal_net, proxy_env
    finally:
        subprocess.run(["docker", "rm", "-f", proxy_name], capture_output=True, text=True)
        subprocess.run(["docker", "network", "rm", internal_net], capture_output=True, text=True)
        subprocess.run(["docker", "network", "rm", egress_net], capture_output=True, text=True)
