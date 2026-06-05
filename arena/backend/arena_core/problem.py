"""Dantzig42 problem data + the authoritative tour-length computation.

The distance MATRIX is the source of truth for scoring (not coordinate geometry),
exactly like the Phase 1 C++ reference solver. Optimal closed-tour length = 699.
"""
from __future__ import annotations

import os
from collections.abc import Sequence

OPTIMAL_LENGTH = 699
NUM_CITIES = 42

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_distance_matrix(path: str | None = None) -> list[list[int]]:
    """Load the 42x42 symmetric integer distance matrix (each line = 42 ints, no label)."""
    path = path or os.path.join(_DATA_DIR, "intercityDistance.txt")
    matrix: list[list[int]] = []
    with open(path) as f:
        for line in f:
            row = [int(tok) for tok in line.split()]
            if row:
                matrix.append(row)
    return matrix


def load_coordinates(path: str | None = None) -> list[tuple[float, float]]:
    """Load city (x, y) coordinates. File format per line: `id x y` (3 columns)."""
    path = path or os.path.join(_DATA_DIR, "cityData.txt")
    coords: list[tuple[float, float]] = []
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 3:
                continue
            coords.append((float(parts[1]), float(parts[2])))
    return coords


def tour_length(tour: Sequence[int], matrix: list[list[int]]) -> int:
    """Total CLOSED-tour length. `tour` holds 1-based city ids; `matrix` is 0-indexed."""
    n = len(tour)
    total = 0
    for i in range(n):
        a = tour[i] - 1
        b = tour[(i + 1) % n] - 1
        total += matrix[a][b]
    return total
