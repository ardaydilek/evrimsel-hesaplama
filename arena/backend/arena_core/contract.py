"""Parser for the submission stdout protocol.

Recognized line prefixes (everything else is ignored, so debug prints are harmless):
  TOUR 1 5 3 ...        the tour as 1-based city ids
  LENGTH 709            the solver's own claimed length (optional; re-verified later)
  GEN <gen> <best> <avg>  per-generation stats (optional; enables the animation)
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ParsedResult:
    tour: list[int] | None = None
    claimed_length: float | None = None
    gen_log: list[tuple[int, float, float]] = field(default_factory=list)


def parse_stdout(text: str) -> ParsedResult:
    result = ParsedResult()
    for line in text.splitlines():
        parts = line.split()
        if not parts:
            continue
        tag = parts[0]
        try:
            if tag == "TOUR":
                result.tour = [int(x) for x in parts[1:]]
            elif tag == "LENGTH" and len(parts) >= 2:
                result.claimed_length = float(parts[1])
            elif tag == "GEN" and len(parts) >= 4:
                result.gen_log.append((int(parts[1]), float(parts[2]), float(parts[3])))
        except ValueError:
            # a recognized line with a malformed number is ignored, never fatal
            continue
    return result
