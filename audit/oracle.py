"""Exact reference for the bounding box of a cubic Bezier segment.

Control points are binary64 floats. They are converted to rationals without
rounding, so the reference describes the curve those floats actually define.
Everything is computed in exact rational arithmetic except the square root of
the discriminant, which is bracketed by integers to 2**-BITS and carried as an
interval. The result is a rigorous enclosure of each bound whose width is
at most 3 * 2**-200 times the largest difference between consecutive control
values, far below anything a float can resolve.
"""

from fractions import Fraction
from math import isqrt

BITS = 256
WIDTH = Fraction(1, 2**200)


def _sqrt_bracket(value, bits):
    """Rationals lo <= sqrt(value) <= hi with hi - lo <= 2**-bits."""
    scaled = (value.numerator << (2 * bits)) // value.denominator
    root = isqrt(scaled)
    lo = Fraction(root, 1 << bits)
    exact = root * root * value.denominator == value.numerator << (2 * bits)
    return lo, lo if exact else Fraction(root + 1, 1 << bits)


def _divide(lo, hi, divisor):
    lo, hi = lo / divisor, hi / divisor
    return (lo, hi) if lo <= hi else (hi, lo)


def stationary_brackets(p):
    """Brackets [lo, hi] within [0, 1] that contain every stationary
    parameter of the scalar cubic with rational controls p in (0, 1)."""
    d0, d1, d2 = p[1] - p[0], p[2] - p[1], p[3] - p[2]
    # B'(t)/3 = a t^2 + b t + c
    a, b, c = d0 - 2 * d1 + d2, 2 * (d1 - d0), d0
    if a == 0:
        if b == 0:
            return []
        brackets = [(-c / b, -c / b)]
    else:
        disc = b * b - 4 * a * c
        if disc < 0:
            return []
        bits = BITS
        while True:
            lo, hi = _sqrt_bracket(disc, bits)
            brackets = [_divide(-b - hi, -b - lo, 2 * a),
                        _divide(-b + lo, -b + hi, 2 * a)]
            inside = [(l, h) for l, h in brackets if h > 0 and l < 1]
            if all(h - l <= WIDTH for l, h in inside):
                break
            bits *= 2
    return [(max(lo, Fraction(0)), min(hi, Fraction(1)))
            for lo, hi in brackets if hi > 0 and lo < 1]


def evaluate(p, t):
    """Exact value of the cubic at rational t (de Casteljau)."""
    s = 1 - t
    q = [s * p[i] + t * p[i + 1] for i in range(3)]
    r = [s * q[i] + t * q[i + 1] for i in range(2)]
    return s * r[0] + t * r[1]


def scalar_range(controls):
    """Enclosure of the range of a scalar cubic over [0, 1].

    Returns (lo, hi, slack): the true minimum lies in [lo - slack, lo] and
    the true maximum in [hi, hi + slack]. lo and hi are values the curve
    attains, so a box that excludes either one excludes part of the curve.
    """
    p = [Fraction(v) for v in controls]
    values = [p[0], p[3]]
    slope = 3 * max(abs(p[i + 1] - p[i]) for i in range(3))  # max |B'| on [0, 1]
    slack = Fraction(0)
    for lo, hi in stationary_brackets(p):
        values.append(evaluate(p, lo))
        slack = max(slack, (hi - lo) * slope)
    return min(values), max(values), slack


def bbox(curve):
    """Exact box (xmin, ymin, xmax, ymax) of a cubic given as eight floats
    x0, y0, x1, y1, x2, y2, x3, y3, together with the enclosure slack."""
    xlo, xhi, xs = scalar_range(curve[0::2])
    ylo, yhi, ys = scalar_range(curve[1::2])
    return (xlo, ylo, xhi, yhi), max(xs, ys)
