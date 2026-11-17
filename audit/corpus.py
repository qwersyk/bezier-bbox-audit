"""Deterministic test curves. Each curve is eight floats x0, y0, ..., x3, y3.

Four families, COUNT curves per column:

general    Eight independent uniform coordinates in [0, 10**k]. Nothing
           special about these curves.
quadratic  A random quadratic segment in the same square, written as a cubic
           with the usual conversion c1 = q0 + 2/3 (q1 - q0),
           c2 = q2 + 2/3 (q1 - q2), evaluated in floats. This is what a
           renderer or converter holds after turning a `Q` command, a
           TrueType outline or a quadraticCurveTo call into a cubic.
symmetric  A mirror-symmetric arch in the same square, with coordinates given
           to eight significant decimal digits.
offset     A general curve from the unit square, translated by 10**k along
           both axes: a small curve far from the origin.

k runs over RANGES for the first three families and over OFFSETS for the last.
"""

import hashlib
import json
import random

SEED = 20261116

# The quadratic segment used for illustration. Its rightmost point is at
# t = 6/11 and its lowest at t = 3/4; the exact box is
# (300000, 150000, 6900000/11, 600000).
EXAMPLE = [300000.0, 600000.0, 900000.0, 0.0, 400000.0, 200000.0]
FAMILIES = ("general", "quadratic", "symmetric", "offset")
RANGES = (-6, -4, -2, 0, 2, 4, 6)
OFFSETS = (0, 2, 4, 6, 8, 10)
COUNT = 1000


def columns(family):
    """The exponents k a family is generated for."""
    return OFFSETS if family == "offset" else RANGES


def power(k):
    """10**k as the correctly rounded float."""
    return float(f"1e{k}")


def _general(rng, k):
    return [rng.uniform(0, power(k)) for _ in range(8)]


def raise_degree(q):
    """The cubic that equals the quadratic q = [x0, y0, x1, y1, x2, y2]."""
    curve = [q[0], q[1]]
    for axis in (0, 1):
        curve.append(q[axis] + 2 / 3 * (q[2 + axis] - q[axis]))
    for axis in (0, 1):
        curve.append(q[4 + axis] + 2 / 3 * (q[2 + axis] - q[4 + axis]))
    return curve + [q[4], q[5]]


def quadratics(k, count=COUNT):
    """The quadratic segments behind the `quadratic` family."""
    rng = random.Random(f"{SEED}/quadratic/{k}")
    return [[rng.uniform(0, power(k)) for _ in range(6)] for _ in range(count)]


def _quadratic(rng, k):
    return raise_degree([rng.uniform(0, power(k)) for _ in range(6)])


def _symmetric(rng, k):
    def decimal(n):
        return float(f"{n}e{k - 8}")

    width = rng.randint(10**6, 5 * 10**7)
    x, inset = decimal(rng.randint(0, 5 * 10**7)), decimal(rng.randint(0, width // 2))
    y, top = decimal(rng.randint(0, 10**8)), decimal(rng.randint(0, 10**8))
    width = decimal(width)
    return [x, y, x + inset, top, x + width - inset, top, x + width, y]


def _offset(rng, k):
    return [power(k) + rng.uniform(0, 1) for _ in range(8)]


_GENERATORS = {"general": _general, "quadratic": _quadratic,
               "symmetric": _symmetric, "offset": _offset}


def curves(family, k, count=COUNT):
    rng = random.Random(f"{SEED}/{family}/{k}")
    return [_GENERATORS[family](rng, k) for _ in range(count)]


def cases():
    """Yield (family, k, curves) for the whole corpus."""
    for family in FAMILIES:
        for k in columns(family):
            yield family, k, curves(family, k)


def digest():
    """SHA-256 of the corpus, to confirm that two runs used the same curves."""
    h = hashlib.sha256()
    for family, k, batch in cases():
        h.update(json.dumps([family, k, [[v.hex() for v in c] for c in batch]]).encode())
    return h.hexdigest()
