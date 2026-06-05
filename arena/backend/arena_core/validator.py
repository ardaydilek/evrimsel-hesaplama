"""Validate that a tour is a legal permutation of all cities (1..N)."""
from __future__ import annotations

from collections.abc import Sequence


def is_valid_tour(tour: Sequence[int] | None, num_cities: int) -> tuple[bool, str]:
    """Return (is_valid, reason). reason is "" when valid.

    A tour is legal iff it lists every city id 1..num_cities exactly once.
    The reason string is human-readable because it surfaces to submitters.
    """
    if tour is None:
        return False, "no TOUR line found in output"
    if len(tour) != num_cities:
        return False, f"tour has {len(tour)} cities, expected {num_cities}"
    if sorted(tour) != list(range(1, num_cities + 1)):
        return False, "tour is not a permutation of cities 1..N (duplicate or out-of-range)"
    return True, ""
