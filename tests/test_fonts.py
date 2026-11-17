"""Reading quadratic segments from glyph outlines."""

import pytest

from audit import fonts, report, run


def test_turns():
    assert fonts.turns([0, 0, 2, 1, 1, 2])  # x goes to 2 and back to 1
    assert fonts.turns([0, 0, 1, 2, 2, 0])  # y rises and falls
    assert not fonts.turns([0, 0, 1, 1, 2, 2])
    assert not fonts.turns([0, 0, 0, 1, 1, 1])  # ends flat, does not turn


def test_off_curve_runs_are_split_at_implied_points():
    pytest.importorskip("fontTools")
    pen = fonts.recorder()
    pen.moveTo((0, 0))
    pen.lineTo((0, 2))
    pen.qCurveTo((1, 4), (3, 4), (4, 2))  # two off-curve points, one implied between them
    pen.closePath()
    assert pen.segments == [[0, 2, 1, 4, 2, 4], [2, 4, 3, 4, 4, 2]]


def test_bundled_fonts():
    pytest.importorskip("fontTools")
    pytest.importorskip("matplotlib")
    described, outlines = fonts.load()
    assert list(outlines) == list(fonts.FONTS)
    for name, segments in outlines.items():
        assert described["fonts"][name]["segments"] == len(segments) > 10_000
        assert 0 < described["fonts"][name]["turning"] < len(segments)
        assert all(len(q) == 6 for q in segments)


def test_table():
    cell = {"wrong": 7, "failed": 0}
    results = {
        "glyphs": {"source": "a package", "fonts": {"Some Font": {"segments": 1000, "turning": 25}}},
        "libraries": {
            "one": {"cells": {run.GLYPHS: {"Some Font": cell},
                              run.GLYPHS_OWN: {"Some Font": {"wrong": 0, "failed": 2}}}},
            "two": {"cells": {run.GLYPHS: {"Some Font": cell}}},
            "clean": {"cells": {run.GLYPHS: {"Some Font": {"wrong": 0, "failed": 0}}}},
        },
    }
    lines = report.glyphs(results)
    assert "Some Font (1,000 segments, 25 of which turn around inside the segment, 2.5%)" in lines[0]
    assert lines[-2:] == ["| one | 7 | 0, 2 failed |", "| two | 7 |  |"]
