"""The measuring code of the audit, without any library under test."""

import pytest

from audit import oracle, report, run

THIN = [0.0, 0.0, 1 / 3, 1e-4, 2 / 3, 1e-4, 1.0, 0.0]


def cell(curve, box, resolution=None):
    return run.measure([curve], [oracle.bbox(curve)[0]], [box], resolution)


def test_exact_box_is_right():
    exact = [float(v) for v in oracle.bbox(THIN)[0]]
    assert cell(THIN, exact)["wrong"] == 0
    assert cell(THIN, exact)["wrong_sampled"] == 0


def test_losing_the_short_axis_is_wrong():
    # The whole height is missing, though it is 0.0075% of the width.
    result = cell(THIN, [0.0, 0.0, 1.0, 0.0])
    assert result["wrong"] == result["wrong_sampled"] == 1
    assert result["worst_short"] == 1
    assert result["wrong_above"] == [1, 1]


def test_misses_are_counted_by_size():
    # The exact height is 7.5e-5; these boxes lose 0.5%, 5% and 50% of it.
    for lost, above in ((0.005, [0, 0]), (0.05, [1, 0]), (0.5, [1, 1])):
        result = cell(THIN, [0.0, 0.0, 1.0, 7.5e-5 * (1 - lost)])
        assert result["wrong"] == 1 and result["wrong_above"] == above
    assert "wrong_above" not in cell(THIN, [0.0, 0.0, 1.0, 7.5e-5])


def test_resolution_is_allowed():
    assert cell(THIN, [0.0, 0.0, 1.0, 0.0], lambda largest: 1e-4)["wrong"] == 0


def test_zero_extent():
    line = [0.0, 5.0, 1.0, 5.0, 2.0, 5.0, 3.0, 5.0]
    assert cell(line, [0.0, 5.0, 3.0, 5.0])["wrong"] == 0
    assert cell(line, [0.0, 5.5, 3.0, 6.0])["wrong"] == 1


def test_too_large_is_recorded_separately():
    result = cell(THIN, [-1.0, 0.0, 1.0, 7.5e-5])
    assert result["wrong"] == 0 and result["worst_excess"] == 1


def test_curves_beyond_a_library_limit_are_set_aside():
    result = run.measure([THIN], [oracle.bbox(THIN)[0]], [[9.0, 9.0, 9.0, 9.0]], limit=0.5)
    assert (result["wrong"], result["unsupported"]) == (0, 1)
    assert report.percent(result, 1) == "n/a"


def test_missing_boxes_are_an_error():
    with pytest.raises(ValueError):
        run.measure([THIN], [oracle.bbox(THIN)[0]], [])
    with pytest.raises(ValueError):
        run.cells([("general", 0, [THIN])], [oracle.bbox(THIN)[0]], [])


def test_comparison_with_a_stored_run():
    def results(library, wrong):
        cell = {"wrong": wrong, "failed": 0}
        return {"corpus": {}, "libraries": {library: {
            "version": "1", "cells": {"general": {"0": cell}}}}}

    assert run.compare(results("Bezier.js", 5), results("Bezier.js", 5)) == 0
    # A count may differ slightly between platforms, not more.
    assert run.compare(results("Bezier.js", 57), results("Bezier.js", 59)) == 0
    assert run.compare(results("Qt", 600), results("Qt", 609)) == 0
    assert run.compare(results("Qt", 600), results("Qt", 700)) == 1
    # A library without wrong boxes must stay without them, unless compiled.
    assert run.compare(results("Bezier.js", 0), results("Bezier.js", 1)) == 1
    assert run.compare(results("Qt", 0), results("Qt", 3)) == 0
    # A library that did not run is a disagreement unless it cannot run here.
    nothing = {"corpus": {}, "libraries": {}}
    assert run.compare(results("Qt", 600), nothing) == 1
    assert run.compare(results("Core Graphics", 0), nothing, ("Core Graphics",)) == 0
    # Other font files are a different input.
    other = dict(results("Bezier.js", 5), glyphs={"source": "another release"})
    assert run.compare(results("Bezier.js", 5), other) == 1


def test_failures_are_counted_and_shown_with_the_wrong_boxes():
    truth = [oracle.bbox(THIN)[0]] * 2
    result = run.measure([THIN, THIN], truth, [None, [0.0, 0.0, 1.0, 0.0]])
    assert (result["wrong"], result["failed"]) == (1, 1)
    assert report.percent(result, 2) == "50%, 1 failed"
