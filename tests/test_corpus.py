"""The corpus is generated, not stored; these pin what is generated."""

from audit import corpus

SHA256 = "e7f70e4f255c87114c1bb451403363a54e9c62490f64cae30c87fd98573aca07"
NONZERO = 915


def test_digest():
    assert corpus.digest() == SHA256


def test_quadratic_family_is_the_raised_quadratics():
    for k in corpus.RANGES:
        raised = [corpus.raise_degree(q) for q in corpus.quadratics(k)]
        assert raised == corpus.curves("quadratic", k)


def test_shapes():
    for family, k, batch in corpus.cases():
        lo, hi = (10.0**k, 10.0**k + 1) if family == "offset" else (0, 10.0**k)
        assert len(batch) == corpus.COUNT
        assert all(len(c) == 8 and all(lo <= v <= hi for v in c) for c in batch)


def test_converted_quadratics_rarely_have_a_zero_leading_coefficient():
    # The cubic coefficient is zero in exact arithmetic. Computed in floats
    # from the stored control points it is rounding error, and rarely zero.
    nonzero = 0
    for c in corpus.curves("quadratic", 0):
        ax = -c[0] + 3 * c[2] - 3 * c[4] + c[6]
        ay = -c[1] + 3 * c[3] - 3 * c[5] + c[7]
        nonzero += ax != 0 or ay != 0
    assert nonzero == NONZERO
