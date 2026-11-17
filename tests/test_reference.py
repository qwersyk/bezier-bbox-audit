"""The floating-point reference against the exact one."""

import json
import math
import random
import shutil
import struct
import subprocess
from pathlib import Path

import pytest

from audit import corpus, oracle
from reference.cubic_bounds import cubic_bounds

ROOT = Path(__file__).resolve().parent.parent

# Largest error allowed, in units in the last place of the largest coordinate.
ULPS = 16


def families():
    for family, k, batch in corpus.cases():
        yield f"{family}/{k}", batch
    rng = random.Random(2)
    yield "tiny", [[rng.uniform(0, 1e-300) for _ in range(8)] for _ in range(500)]
    yield "huge", [[rng.uniform(0, 1e300) for _ in range(8)] for _ in range(500)]
    yield "integers", [[float(rng.randint(0, 3)) for _ in range(8)] for _ in range(2000)]
    yield "mixed", [[rng.choice((-1, 1)) * 10 ** rng.uniform(-8, 8) for _ in range(8)]
                    for _ in range(500)]
    yield "thin", [[rng.uniform(0, 1) * (1e-9 if i % 2 else 1) for i in range(8)]
                   for _ in range(500)]


def error_in_ulps(curve):
    exact, _ = oracle.bbox(curve)
    unit = math.ulp(max(abs(v) for v in curve))
    return max(abs(got - float(want)) for got, want in zip(cubic_bounds(*curve), exact)) / unit


@pytest.mark.parametrize("name,curves", list(families()), ids=lambda v: v if isinstance(v, str) else "")
def test_accuracy(name, curves):
    assert max(error_in_ulps(c) for c in curves) <= ULPS


def test_examples():
    # The quadratic used for illustration, stored as a cubic.
    box = cubic_bounds(*corpus.raise_degree(corpus.EXAMPLE))
    assert box == pytest.approx((300000, 150000, 6900000 / 11, 600000), rel=1e-15)
    # Symmetric arch with its top at t = 1/2.
    box = cubic_bounds(1000, 1030.6, 2000, 5851.4, 3000, 5851.4, 4000, 1030.6)
    assert box == pytest.approx((1000, 1030.6, 4000, 4646.2), rel=1e-15)


def test_near_the_largest_float():
    # Finite input with a finite answer: the top of the arch is at 3/4 of 1e308.
    assert cubic_bounds(0, 0, 0, 1e308, 0, 1e308, 0, 0) == (0, 0, 0, 7.5e307)


def test_thin_curve():
    # The height is 7500 times smaller than the width and must not be lost.
    box = cubic_bounds(0, 0, 1 / 3, 1e-4, 2 / 3, 1e-4, 1, 0)
    assert box == pytest.approx((0, 0, 1, 7.5e-5), rel=1e-15)


def test_degenerate():
    assert cubic_bounds(1, 2, 1, 2, 1, 2, 1, 2) == (1, 2, 1, 2)
    assert cubic_bounds(0, 0, 1, 1, 2, 2, 3, 3) == (0, 0, 3, 3)
    assert cubic_bounds(3, 0, 2, 0, 1, 0, 0, 0) == (0, 0, 3, 0)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_javascript_matches_python():
    curves = [c for _, batch in families() for c in batch]
    script = (
        "import { cubicBounds } from './reference/cubic_bounds.mjs';"
        "import fs from 'fs';"
        "const curves = JSON.parse(fs.readFileSync(0, 'utf8'));"
        "const out = new Float64Array(curves.length * 4);"
        "curves.forEach((c, i) => out.set(cubicBounds(...c), i * 4));"
        "process.stdout.write(Buffer.from(out.buffer).toString('hex'));"
    )
    done = subprocess.run(["node", "--input-type=module", "-e", script], cwd=ROOT,
                          input=json.dumps(curves), capture_output=True, text=True, check=True)
    expected = b"".join(struct.pack("<4d", *cubic_bounds(*c)) for c in curves)
    assert bytes.fromhex(done.stdout) == expected
