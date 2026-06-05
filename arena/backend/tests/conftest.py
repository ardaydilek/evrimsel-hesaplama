import shutil
import subprocess

import pytest


def _docker_ready() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        return subprocess.run(["docker", "info"], capture_output=True, timeout=10).returncode == 0
    except Exception:
        return False


def pytest_collection_modifyitems(config, items):
    if _docker_ready():
        return
    skip = pytest.mark.skip(reason="docker not available")
    for item in items:
        if "docker" in item.keywords:
            item.add_marker(skip)
