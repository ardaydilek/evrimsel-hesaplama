from arena_core import problem
from arena_core.local_runner import LocalRunner
from arena_core.run_spec import RunSpec
from arena_core.scorer import score_stdout

# A minimal "solver" that prints the identity tour 1..42 (a valid permutation;
# its closed-tour length is the Dantzig42 optimum, 699).
SOLVER = "print('TOUR ' + ' '.join(str(c) for c in range(1, 43)))"


def test_local_runner_output_scores_via_scorer():
    run = LocalRunner().run(RunSpec(preset="python", files={"main.py": SOLVER}))
    assert run.status == "ok"

    matrix = problem.load_distance_matrix()
    score = score_stdout(run.stdout, matrix)
    assert score.valid is True
    assert score.length == 699
