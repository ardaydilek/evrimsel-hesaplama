# tests/integration/test_templates.py
#
# Verifies the shipped starter templates end-to-end: each builds, runs in the real
# sandbox, and yields the same valid nearest-neighbor tour. The templates are read from
# the single canonical JSON the frontend also consumes (lib/solver-templates.json), so
# what a submitter receives is exactly what is tested here — no drift.
import json
import pathlib

import pytest

from arena_core import problem
from arena_core.container_runner import ContainerRunner
from arena_core.run_spec import RunSpec
from arena_core.scorer import score_stdout

pytestmark = pytest.mark.docker

_JSON = pathlib.Path(__file__).parents[3] / "frontend" / "lib" / "solver-templates.json"
TEMPLATES = json.loads(_JSON.read_text())
MATRIX = problem.load_distance_matrix()

# Deterministic nearest-neighbor (from city 1, lowest-index tie-break) closed-tour length.
# Every language port must produce the identical tour, so the same length pins them all.
NN_LENGTH = 956


@pytest.mark.parametrize("preset", sorted(TEMPLATES))
def test_starter_template_builds_and_scores(preset):
    files = {f["path"]: f["content"] for f in TEMPLATES[preset]}
    r = ContainerRunner().run(RunSpec(preset=preset, files=files))
    assert r.status == "ok", r.stderr
    score = score_stdout(r.stdout, MATRIX)
    assert score.valid, score.reason
    assert score.length == NN_LENGTH
