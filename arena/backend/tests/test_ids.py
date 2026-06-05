import re

from arena_core.ids import make_submission_id, slugify


def test_slugify_basic():
    assert slugify("Arda Kaan") == "arda-kaan"


def test_slugify_turkish_transliterated():
    assert slugify("Şükrü Çağ") == "sukru-cag"
    assert slugify("ışıl ÖĞ") == "isil-og"


def test_slugify_collapses_and_caps_length():
    assert slugify("  a!!!b  ") == "a-b"
    assert slugify("x" * 50) == "x" * 32


def test_slugify_empty_fallback():
    assert slugify("!!!") == "katilimci"
    assert slugify("") == "katilimci"


def test_make_submission_id_format():
    assert re.fullmatch(r"arda-kaan-[0-9a-f]{6}", make_submission_id("Arda Kaan"))


def test_make_submission_id_unique_enough():
    ids = {make_submission_id("ada") for _ in range(100)}
    assert len(ids) == 100
