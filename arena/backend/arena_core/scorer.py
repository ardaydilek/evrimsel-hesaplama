"""Combine parsing + validation + authoritative length into an official score.

The server NEVER trusts the submitter's claimed LENGTH; it recomputes the tour
length from the canonical distance matrix.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import problem
from .contract import parse_stdout
from .validator import is_valid_tour


@dataclass
class ScoreResult:
    valid: bool
    reason: str                     # "" when valid; failure reason otherwise
    length: int | None              # server-recomputed authoritative length
    claimed_length: float | None    # what the submitter said (for display/diagnostics)
    tour: list[int] | None
    gen_log: list[tuple[int, float, float]]


def score_stdout(text: str, matrix: list[list[int]]) -> ScoreResult:
    parsed = parse_stdout(text)
    ok, reason = is_valid_tour(parsed.tour, problem.NUM_CITIES)
    if not ok:
        return ScoreResult(False, reason, None, parsed.claimed_length,
                           parsed.tour, parsed.gen_log)
    length = problem.tour_length(parsed.tour, matrix)
    return ScoreResult(True, "", length, parsed.claimed_length,
                       parsed.tour, parsed.gen_log)
