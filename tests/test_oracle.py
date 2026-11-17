"""The exact reference, checked against cases with known answers and against
direct evaluation of the curve."""

import random
from fractions import Fraction

from audit import oracle


def test_known_extrema():
    # 3t(1-t): maximum 3/4 at t = 1/2.
    assert oracle.scalar_range([0.0, 1.0, 1.0, 0.0])[:2] == (0, Fraction(3, 4))
    # t^3: monotone, stationary only at the end point.
    assert oracle.scalar_range([0.0, 0.0, 0.0, 1.0])[:2] == (0, 1)
    # Constant and linear.
    assert oracle.scalar_range([2.0, 2.0, 2.0, 2.0]) == (2, 2, 0)
    assert oracle.scalar_range([0.0, 1.0, 2.0, 3.0]) == (0, 3, 0)
    # (2t-1)^3: stationary at t = 1/2 without being an extremum.
    assert oracle.scalar_range([-1.0, 1.0, -1.0, 1.0])[:2] == (-1, 1)


def test_irrational_stationary_point():
    # Controls 0, 1, 2, 0 give 3t - 3t^3 with maximum 2/sqrt(3) at t = 1/sqrt(3).
    lo, hi, slack = oracle.scalar_range([0.0, 1.0, 2.0, 0.0])
    assert lo == 0
    assert slack < Fraction(1, 2**190)
    assert hi * hi <= Fraction(4, 3) <= (hi + slack) ** 2


def test_quadratic_written_as_cubic():
    # The exact cubic form of the quadratic 0, 7000, 5000: maximum 49000/9 at t = 7/9.
    q = [Fraction(0), Fraction(7000), Fraction(5000)]
    cubic = [q[0], q[0] + Fraction(2, 3) * (q[1] - q[0]),
             q[2] + Fraction(2, 3) * (q[1] - q[2]), q[2]]
    assert oracle.scalar_range(cubic) == (0, Fraction(49000, 9), 0)


def test_encloses_sampled_points():
    rng = random.Random(1)
    for _ in range(300):
        scale = 10.0 ** rng.randint(-200, 200)
        controls = [rng.uniform(-scale, scale) for _ in range(4)]
        lo, hi, slack = oracle.scalar_range(controls)
        p = [Fraction(v) for v in controls]
        samples = [oracle.evaluate(p, Fraction(i, 64)) for i in range(65)]
        assert lo - slack <= min(samples) and max(samples) <= hi + slack
        # Both bounds are values the curve attains.
        assert min(p) <= lo <= hi <= max(p)


def test_bbox_layout():
    # x = 4t^3; y = 9(1-t)^3 + t^3, with minimum 9/16 at t = 3/4.
    box, slack = oracle.bbox([0.0, 9.0, 0.0, 0.0, 0.0, 0.0, 4.0, 1.0])
    assert box == (0, Fraction(9, 16), 4, 9) and slack == 0
