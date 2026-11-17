"""Quadratic segments of real glyph outlines.

The fonts are the ones installed with matplotlib, so nothing is downloaded.
Every simple (not composite) TrueType glyph is read in font units, and each
run of off-curve points is split at the implied on-curve points into
quadratic segments [x0, y0, x1, y1, x2, y2].
"""

import hashlib
from importlib import metadata
from pathlib import Path

FONTS = {"DejaVu Sans": "DejaVuSans.ttf", "DejaVu Sans Oblique": "DejaVuSans-Oblique.ttf"}


def turns(q):
    """Whether a coordinate of the quadratic segment has an extremum strictly
    inside the segment."""
    return any((q[2 + axis] - q[axis]) * (q[4 + axis] - q[2 + axis]) < 0 for axis in (0, 1))


def recorder(glyphs=None):
    """A fontTools pen that collects quadratic segments in `segments`."""
    from fontTools.pens.basePen import BasePen

    class Recorder(BasePen):
        def __init__(self):
            super().__init__(glyphs)
            self.segments = []

        def _moveTo(self, point):
            pass

        def _lineTo(self, point):
            pass

        def _qCurveToOne(self, control, end):
            start = self._getCurrentPoint()
            self.segments.append([float(v) for v in (*start, *control, *end)])

    return Recorder()


def segments(path):
    from fontTools.ttLib import TTFont

    font = TTFont(path)
    glyphs, pen = font.getGlyphSet(), recorder()
    for name in font.getGlyphOrder():
        glyph = font["glyf"][name]
        if glyph.numberOfContours > 0:  # composites have -1, empty glyphs 0
            glyphs[name].draw(pen)
    return pen.segments


def load():
    """(description, {font name: segments}). The description identifies the
    files and is stored with the results."""
    import matplotlib

    folder = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    described, found = {}, {}
    for name, file in FONTS.items():
        found[name] = segments(folder / file)
        described[name] = {
            "file": file,
            "sha256": hashlib.sha256((folder / file).read_bytes()).hexdigest(),
            "segments": len(found[name]),
            "turning": sum(map(turns, found[name])),
        }
    return {"source": f"matplotlib {metadata.version('matplotlib')}", "fonts": described}, found
