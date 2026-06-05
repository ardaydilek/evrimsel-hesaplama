"""Submission ID generation: a readable, handle-derived, collision-resistant slug id.

e.g. handle "Arda Kaan" -> "arda-kaan-3f9a1c". URL/path-safe; Turkish letters are
transliterated so the slug stays within [a-z0-9-].
"""
from __future__ import annotations

import re
import secrets

# Map Turkish letters to ASCII before slugifying (so "Şükrü" -> "sukru", not "-k-r").
_TR = str.maketrans({
    "ş": "s", "Ş": "s", "ı": "i", "İ": "i", "ö": "o", "Ö": "o",
    "ü": "u", "Ü": "u", "ğ": "g", "Ğ": "g", "ç": "c", "Ç": "c",
})


def slugify(handle: str) -> str:
    """Lowercase, transliterate Turkish, reduce to [a-z0-9-]; cap 32 chars."""
    s = handle.translate(_TR).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = s[:32].strip("-")
    return s or "katilimci"


def make_submission_id(handle: str) -> str:
    """`<handle-slug>-<6 hex>` — readable and collision-resistant."""
    return f"{slugify(handle)}-{secrets.token_hex(3)}"
