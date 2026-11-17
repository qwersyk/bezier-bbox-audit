"""Smallest reproductions for the Python-callable libraries.

    python repro/python.py

Every case uses the quadratic segment (300000, 600000) (900000, 0)
(400000, 200000). Its rightmost point is at t = 6/11, x = 6900000/11 =
627272.73; its lowest point is at t = 3/4, y = 150000. The exact box is
therefore (300000, 150000, 627272.73, 600000).
"""

Q = (300000.0, 600000.0, 900000.0, 0.0, 400000.0, 200000.0)
EXACT = (300000.0, 150000.0, 6900000 / 11, 600000.0)


def as_cubic(q):
    """The cubic a converter stores for the quadratic q."""
    x0, y0, x1, y1, x2, y2 = q
    return (x0, y0,
            x0 + 2 / 3 * (x1 - x0), y0 + 2 / 3 * (y1 - y0),
            x2 + 2 / 3 * (x1 - x2), y2 + 2 / 3 * (y1 - y2),
            x2, y2)


def svgpathtools(q):
    from svgpathtools import CubicBezier
    c = as_cubic(q)
    xmin, xmax, ymin, ymax = CubicBezier(*[complex(c[i], c[i + 1]) for i in (0, 2, 4, 6)]).bbox()
    return xmin, ymin, xmax, ymax


def svg_path(q):
    from svg.path import CubicBezier
    c = as_cubic(q)
    return CubicBezier(*[complex(c[i], c[i + 1]) for i in (0, 2, 4, 6)]).boundingbox()


def fonttools(q):
    from fontTools.misc.bezierTools import calcCubicBounds
    c = as_cubic(q)
    return calcCubicBounds(*[(c[i], c[i + 1]) for i in (0, 2, 4, 6)])


def beziers(q):
    from beziers.cubicbezier import CubicBezier
    from beziers.point import Point
    c = as_cubic(q)
    b = CubicBezier(*[Point(c[i], c[i + 1]) for i in (0, 2, 4, 6)]).bounds()
    return b.left, b.bottom, b.right, b.top


def qt(q):
    from PySide6.QtGui import QPainterPath
    path = QPainterPath()
    path.moveTo(q[0], q[1])
    path.quadTo(*q[2:])
    r = path.boundingRect()
    return r.left(), r.top(), r.right(), r.bottom()


CASES = [
    ("svgpathtools  CubicBezier.bbox", svgpathtools),
    ("svg.path  CubicBezier.boundingbox", svg_path),
    ("fontTools  calcCubicBounds", fonttools),
    ("beziers.py  CubicBezier.bounds", beziers),
    ("Qt  QPainterPath.quadTo + boundingRect", qt),
]

if __name__ == "__main__":
    print("exact", list(EXACT))
    for name, box in CASES:
        try:
            got = [float(v) for v in box(Q)]
        except ImportError as error:
            print(f"{name}: not installed ({error.name})")
            continue
        miss = max(got[0] - EXACT[0], got[1] - EXACT[1], EXACT[2] - got[2], EXACT[3] - got[3])
        print(f"{name}\n  {got}\n  the curve leaves the box by {miss:.0f}")
