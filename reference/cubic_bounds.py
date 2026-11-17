"""Bounding box of a cubic Bezier segment in ordinary floating point.

The stationary points of one coordinate are the roots of

    a t^2 + 2 h t + c,   a = d0 - 2 d1 + d2,  h = d1 - d0,  c = d0,

where d0, d1, d2 are the differences of consecutive control values. The
textbook formula (-h +- sqrt(h^2 - a c)) / a subtracts two nearly equal
numbers for one of the roots whenever a is small, and divides the remainder
by a. Here the sum that cannot cancel is formed first, q = -(h + sign(h)
sqrt(h^2 - a c)), and the roots are taken as q / a and c / q. Nothing has to
be compared with zero up to a tolerance: when a is exactly zero, c / q is the
root of the remaining linear equation.

Inputs must be finite, and so must the differences of the control values and
four times those differences; coordinates below 1e307 in magnitude always are.
"""

from math import copysign, sqrt


def cubic_range(p0, p1, p2, p3):
    """Minimum and maximum over 0 <= t <= 1 of the cubic Bezier polynomial
    with control values p0, p1, p2, p3."""
    d0, d1, d2 = p1 - p0, p2 - p1, p3 - p2
    a, h, c = d0 - 2 * d1 + d2, d1 - d0, d0
    lo, hi = (p0, p3) if p0 <= p3 else (p3, p0)
    scale = max(abs(a), abs(h), abs(c))
    if scale == 0:
        return lo, hi
    # The roots do not depend on a common factor; dividing it out keeps the
    # squares below from overflowing or underflowing.
    sa, sh, sc = a / scale, h / scale, c / scale
    disc = sh * sh - sa * sc
    if disc >= 0:
        q = -(sh + copysign(sqrt(disc), sh))
        for numerator, denominator in ((q, sa), (sc, q)):
            if denominator != 0:
                t = numerator / denominator
                if 0 < t < 1:
                    # de Casteljau: every step is a weighted mean, so nothing
                    # overflows.
                    s = 1 - t
                    q0, q1, q2 = s * p0 + t * p1, s * p1 + t * p2, s * p2 + t * p3
                    value = s * (s * q0 + t * q1) + t * (s * q1 + t * q2)
                    lo, hi = min(lo, value), max(hi, value)
    return lo, hi


def cubic_bounds(x0, y0, x1, y1, x2, y2, x3, y3):
    """Bounding box (xmin, ymin, xmax, ymax) of a cubic Bezier segment."""
    xmin, xmax = cubic_range(x0, x1, x2, x3)
    ymin, ymax = cubic_range(y0, y1, y2, y3)
    return xmin, ymin, xmax, ymax
