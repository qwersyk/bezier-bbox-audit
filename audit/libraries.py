"""Adapters for the Python-callable libraries under test.

Each entry maps a display name to (distribution, entry point, factory). The
factory imports the library and returns a function that takes one curve
(eight floats) and returns its box as (xmin, ymin, xmax, ymax). A library that
is not installed is skipped by the runner.
"""


def _points(c):
    return [(c[0], c[1]), (c[2], c[3]), (c[4], c[5]), (c[6], c[7])]


def _complex(c):
    return [complex(x, y) for x, y in _points(c)]


def _svgpathtools():
    from svgpathtools import CubicBezier

    def box(c):
        xmin, xmax, ymin, ymax = CubicBezier(*_complex(c)).bbox()
        return xmin, ymin, xmax, ymax
    return box


def _svg_path():
    from svg.path import CubicBezier
    return lambda c: CubicBezier(*_complex(c)).boundingbox()


def _svgelements():
    from svgelements import CubicBezier
    return lambda c: CubicBezier(*_complex(c)).bbox()


def _fonttools():
    from fontTools.misc.bezierTools import calcCubicBounds
    return lambda c: calcCubicBounds(*_points(c))


def _matplotlib():
    from matplotlib.path import Path
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

    def box(c):
        e = Path(_points(c), codes).get_extents()
        return e.x0, e.y0, e.x1, e.y1
    return box


def _beziers():
    from beziers.cubicbezier import CubicBezier
    from beziers.point import Point

    def box(c):
        b = CubicBezier(*[Point(x, y) for x, y in _points(c)]).bounds()
        return b.left, b.bottom, b.right, b.top
    return box


def _inkex():
    import inkex

    def box(c):
        b = inkex.Path("M %r %r C %r %r %r %r %r %r" % tuple(c)).bounding_box()
        return b.left, b.top, b.right, b.bottom
    return box


def _kurbo():
    from kurbopy import CubicBez, Point

    def box(c):
        r = CubicBez(*[Point(x, y) for x, y in _points(c)]).bounding_box()
        return r.min_x(), r.min_y(), r.max_x(), r.max_y()
    return box


def _skia():
    import skia

    def box(c):
        path = skia.Path()
        path.moveTo(c[0], c[1])
        path.cubicTo(*c[2:])
        r = path.computeTightBounds()
        return r.left(), r.top(), r.right(), r.bottom()
    return box


def _qt():
    from PySide6.QtGui import QPainterPath

    def box(c):
        path = QPainterPath()
        path.moveTo(c[0], c[1])
        path.cubicTo(*c[2:])
        r = path.boundingRect()
        return r.left(), r.top(), r.right(), r.bottom()
    return box


def _cairo():
    import cairo
    surface = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, None)

    def box(c):
        ctx = cairo.Context(surface)
        ctx.move_to(c[0], c[1])
        ctx.curve_to(*c[2:])
        return ctx.path_extents()
    return box


def _coregraphics():
    import Quartz

    def box(c):
        path = Quartz.CGPathCreateMutable()
        Quartz.CGPathMoveToPoint(path, None, c[0], c[1])
        Quartz.CGPathAddCurveToPoint(path, None, *c[2:])
        r = Quartz.CGPathGetPathBoundingBox(path)
        return (r.origin.x, r.origin.y,
                r.origin.x + r.size.width, r.origin.y + r.size.height)
    return box


LIBRARIES = {
    "svgpathtools": ("svgpathtools", "CubicBezier.bbox", _svgpathtools),
    "svg.path": ("svg.path", "CubicBezier.boundingbox", _svg_path),
    "svgelements": ("svgelements", "CubicBezier.bbox", _svgelements),
    "fontTools": ("fonttools", "bezierTools.calcCubicBounds", _fonttools),
    "matplotlib": ("matplotlib", "Path.get_extents", _matplotlib),
    "beziers.py": ("beziers", "CubicBezier.bounds", _beziers),
    "inkex": ("inkex", "Path.bounding_box", _inkex),
    "kurbo": ("kurbopy", "CubicBez.bounding_box", _kurbo),
    "Skia": ("skia-python", "Path.computeTightBounds", _skia),
    "Qt": ("PySide6-Essentials", "QPainterPath.boundingRect", _qt),
    "cairo": ("pycairo", "Context.path_extents", _cairo),
    "Core Graphics": ("pyobjc-framework-Quartz", "CGPathGetPathBoundingBox", _coregraphics),
}


def _qt_quadratic():
    from PySide6.QtGui import QPainterPath

    def box(q):
        path = QPainterPath()
        path.moveTo(q[0], q[1])
        path.quadTo(*q[2:])
        r = path.boundingRect()
        return r.left(), r.top(), r.right(), r.bottom()
    return box


# Entry points that take a quadratic segment (six floats) and convert it to a
# cubic internally before computing the box.
QUADRATIC = {
    "Qt": ("QPainterPath.quadTo", _qt_quadratic),
}
