# Results

Corpus seed 20261116, SHA-256 `e7f70e4f255c87114c1bb451403363a54e9c62490f64cae30c87fd98573aca07`, 1000 curves per cell. A box is wrong when, along either axis, the curve extends beyond it by more than 0.001 of its extent along that axis. Columns are the upper end of the coordinate range, or for the offset family the distance from the origin. Python 3.13.13, Node 26.12.0, macOS-27.3-arm64-arm-64bit-Mach-O.

## Versions

| Library | Implementation | Tested through |
|---|---|---|
| svgpathtools | Python | svgpathtools 1.8.0 |
| svg.path | Python | svg.path 7.1 |
| svgelements | Python | svgelements 1.9.6 |
| fontTools | Python | fonttools 4.68.0 |
| matplotlib | Python | matplotlib 3.11.2 |
| beziers.py | Python | beziers 0.6.0 |
| inkex | Python | inkex 1.4.1 |
| kurbo | Rust | kurbopy 0.13.1 |
| Skia | C++ | skia-python 144.1 |
| Qt | C++ | PySide6-Essentials 6.12.0 |
| cairo | C | pycairo 1.29.2 (cairo 1.18.6) |
| Core Graphics | C | pyobjc-framework-Quartz 13.0 (macOS 27.3) |
| fabric.js | JavaScript | fabric 7.4.0 |
| opentype.js | JavaScript | opentype.js 2.0.0 |
| Bezier.js | JavaScript | bezier-js 6.1.4 |
| PDF.js | JavaScript | pdfjs-dist 6.5.438 |
| Paper.js | JavaScript | paper 0.17.0 |
| Two.js | JavaScript | two.js 0.8.24 |
| ZRender | JavaScript | zrender 6.1.0 |
| Konva | JavaScript | konva 10.9.1 |
| AntV G | JavaScript | @antv/g-math 3.1.0 |
| Snap.svg | JavaScript | snapsvg 0.5.1 |
| Raphael | JavaScript | raphael 2.3.0 |
| svg-path-bbox | JavaScript | svg-path-bbox 2.1.0 |
| svg-path-commander | JavaScript | svg-path-commander 2.3.5 |
| thi.ng/geom-splines | JavaScript | @thi.ng/geom-splines 2.3.95 |
| OpenJDK | Java | java.desktop 25.0.1 |

## General

| Library | Entry point | 10⁻⁶ | 10⁻⁴ | 10⁻² | 1 | 10² | 10⁴ | 10⁶ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| svgpathtools | `CubicBezier.bbox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| svg.path | `CubicBezier.boundingbox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| svgelements | `CubicBezier.bbox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fontTools | `bezierTools.calcCubicBounds` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| matplotlib | `Path.get_extents` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| beziers.py | `CubicBezier.bounds` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| inkex | `Path.bounding_box` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| kurbo | `CubicBez.bounding_box` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Skia | `Path.computeTightBounds` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Qt | `QPainterPath.boundingRect` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cairo | `Context.path_extents` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Core Graphics | `CGPathGetPathBoundingBox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fabric.js | `util.getBoundsOfCurve` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| opentype.js | `Path.getBoundingBox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Bezier.js | `Bezier.bbox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| PDF.js | `Util.bezierBoundingBox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Paper.js | `Path.bounds` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Two.js | `getCurveBoundingBox` | 90% | 90% | 0.4% | 0 | 0 | 0 | 0 |
| ZRender | `bbox.fromCubic` | 90% | 8.5% | 0 | 0 | 0 | 0 | 0 |
| Konva | `Path.getSelfRect` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AntV G | `cubicBox` | 90% | 89% | 0.5% | 0 | 0 | 0 | 0 |
| Snap.svg | `Snap.path.getBBox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Raphael | `Raphael.pathBBox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| svg-path-bbox | `svgPathBbox` | 0.2% | 0 | 0 | 0 | 0 | 0 | 0 |
| svg-path-commander | `getPathBBox` | 0.2% | 0 | 0 | 0 | 0 | 0 | 0 |
| thi.ng/geom-splines | `cubicBounds` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| OpenJDK | `CubicCurve2D.getBounds2D` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Quadratic

| Library | Entry point | 10⁻⁶ | 10⁻⁴ | 10⁻² | 1 | 10² | 10⁴ | 10⁶ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| svgpathtools | `CubicBezier.bbox` | 0 | 0 | 0 | 0 | 0 | 50% | 79% |
| svg.path | `CubicBezier.boundingbox` | 68% | 67% | 69% | 63% | 65% | 68% | 70% |
| svgelements | `CubicBezier.bbox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fontTools | `bezierTools.calcCubicBounds` | 0 | 0 | 0 | 0 | 0 | 0 | 54% |
| matplotlib | `Path.get_extents` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| beziers.py | `CubicBezier.bounds` | 83% | 83% | 84% | 82% | 81% | 82% | 85% |
| inkex | `Path.bounding_box` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| kurbo | `CubicBez.bounding_box` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Skia | `Path.computeTightBounds` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Qt | `QPainterPath.boundingRect` | 0 | 0 | 0 | 0 | 0 | 60% | 66% |
| cairo | `Context.path_extents` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Core Graphics | `CGPathGetPathBoundingBox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fabric.js | `util.getBoundsOfCurve` | 0 | 0 | 0 | 0 | 0 | 59% | 62% |
| opentype.js | `Path.getBoundingBox` | 60% | 63% | 66% | 59% | 61% | 62% | 63% |
| Bezier.js | `Bezier.bbox` | 68% | 68% | 70% | 63% | 66% | 69% | 71% |
| PDF.js | `Util.bezierBoundingBox` | 0 | 0 | 0 | 0 | 0 | 61% | 64% |
| Paper.js | `Path.bounds` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Two.js | `getCurveBoundingBox` | 88% | 89% | 0.8% | 0 | 0 | 0 | 0 |
| ZRender | `bbox.fromCubic` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Konva | `Path.getSelfRect` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AntV G | `cubicBox` | 88% | 0.3% | 0 | 0 | 0 | 0 | 0 |
| Snap.svg | `Snap.path.getBBox` | 0 | 0 | 0 | 0 | 0 | 59% | 62% |
| Raphael | `Raphael.pathBBox` | 79% | 79% | 79% | 79% | 78% | 79% | 81% |
| svg-path-bbox | `svgPathBbox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| svg-path-commander | `getPathBBox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| thi.ng/geom-splines | `cubicBounds` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| OpenJDK | `CubicCurve2D.getBounds2D` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Symmetric

| Library | Entry point | 10⁻⁶ | 10⁻⁴ | 10⁻² | 1 | 10² | 10⁴ | 10⁶ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| svgpathtools | `CubicBezier.bbox` | 0 | 0 | 0 | 0 | 0 | 9.3% | 43% |
| svg.path | `CubicBezier.boundingbox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| svgelements | `CubicBezier.bbox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fontTools | `bezierTools.calcCubicBounds` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| matplotlib | `Path.get_extents` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| beziers.py | `CubicBezier.bounds` | 100% | 100% | 100% | 100% | 100% | 100% | 100% |
| inkex | `Path.bounding_box` | 0.2% | 0 | 0 | 0 | 0 | 0 | 0 |
| kurbo | `CubicBez.bounding_box` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Skia | `Path.computeTightBounds` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Qt | `QPainterPath.boundingRect` | 0 | 0 | 0 | 0 | 0 | 28% | 37% |
| cairo | `Context.path_extents` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Core Graphics | `CGPathGetPathBoundingBox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fabric.js | `util.getBoundsOfCurve` | 0 | 0 | 0 | 0 | 0 | 13% | 22% |
| opentype.js | `Path.getBoundingBox` | 21% | 19% | 19% | 22% | 19% | 18% | 22% |
| Bezier.js | `Bezier.bbox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| PDF.js | `Util.bezierBoundingBox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Paper.js | `Path.bounds` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Two.js | `getCurveBoundingBox` | 100% | 100% | 2.6% | 0 | 0 | 0 | 0 |
| ZRender | `bbox.fromCubic` | 0.5% | 0 | 0 | 0 | 0 | 0 | 0 |
| Konva | `Path.getSelfRect` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AntV G | `cubicBox` | 100% | 3.8% | 0 | 0 | 0 | 0 | 0 |
| Snap.svg | `Snap.path.getBBox` | 0 | 0 | 0 | 0 | 0 | 13% | 22% |
| Raphael | `Raphael.pathBBox` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| svg-path-bbox | `svgPathBbox` | 2.6% | 0 | 0 | 0 | 0 | 0 | 0 |
| svg-path-commander | `getPathBBox` | 2.6% | 0 | 0 | 0 | 0 | 0 | 0 |
| thi.ng/geom-splines | `cubicBounds` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| OpenJDK | `CubicCurve2D.getBounds2D` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Offset

| Library | Entry point | 1 | 10² | 10⁴ | 10⁶ | 10⁸ | 10¹⁰ |
|---|---|---:|---:|---:|---:|---:|---:|
| svgpathtools | `CubicBezier.bbox` | 0 | 0 | 0 | 0.8% | 90% | 90% |
| svg.path | `CubicBezier.boundingbox` | 0 | 0 | 0 | 0 | 0 | 0 |
| svgelements | `CubicBezier.bbox` | 0 | 0 | 0 | 0.8% | 90% | 90% |
| fontTools | `bezierTools.calcCubicBounds` | 0 | 0 | 0 | 0 | 0 | 0 |
| matplotlib | `Path.get_extents` | 0 | 0 | 0 | 0 | 0 | 0 |
| beziers.py | `CubicBezier.bounds` | 0 | 0 | 0 | 0 | 0 | 0 |
| inkex | `Path.bounding_box` | 0 | 0 | 0 | 0 | 0 | 0 |
| kurbo | `CubicBez.bounding_box` | 0 | 0 | 0 | 0 | 0 | 0 |
| Skia | `Path.computeTightBounds` | 0 | 0 | 0 | 0 | 0 | 0 |
| Qt | `QPainterPath.boundingRect` | 0 | 0 | 0 | 0 | 0 | 0 |
| cairo | `Context.path_extents` | 0 | 0 | 0 | 0 | n/a | n/a |
| Core Graphics | `CGPathGetPathBoundingBox` | 0 | 0 | 0 | 0 | 0 | 0 |
| fabric.js | `util.getBoundsOfCurve` | 0 | 0 | 0 | 0 | 0 | 0 |
| opentype.js | `Path.getBoundingBox` | 0 | 0 | 0 | 0 | 0 | 0 |
| Bezier.js | `Bezier.bbox` | 0 | 0 | 0 | 0 | 0 | 0 |
| PDF.js | `Util.bezierBoundingBox` | 0 | 0 | 0 | 0 | 0 | 0 |
| Paper.js | `Path.bounds` | 0 | 0 | 0 | 0 | 0 | 0 |
| Two.js | `getCurveBoundingBox` | 0 | 0 | 0 | 0 | 0 | 0 |
| ZRender | `bbox.fromCubic` | 0 | 0 | 0 | 0 | 0 | 0 |
| Konva | `Path.getSelfRect` | 0 | 0 | 0 | 0 | 0 | 0 |
| AntV G | `cubicBox` | 0 | 0 | 0 | 0 | 0 | 0 |
| Snap.svg | `Snap.path.getBBox` | 0 | 0 | 0 | 0 | 0 | 0 |
| Raphael | `Raphael.pathBBox` | 0 | 0 | 0 | 0 | 0 | 0 |
| svg-path-bbox | `svgPathBbox` | 0 | 0 | 0 | 0.8% | 90% | 90% |
| svg-path-commander | `getPathBBox` | 0 | 0 | 0 | 0.8% | 90% | 90% |
| thi.ng/geom-splines | `cubicBounds` | 0 | 0 | 0 | 0 | 0 | 0 |
| OpenJDK | `CubicCurve2D.getBounds2D` | 0 | 0 | 0 | 0 | 0 | 0 |

## Quadratic, converted by the library

| Library | Entry point | 10⁻⁶ | 10⁻⁴ | 10⁻² | 1 | 10² | 10⁴ | 10⁶ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Qt | `QPainterPath.quadTo` | 0 | 0 | 0 | 0 | 0 | 56% | 63% |
| opentype.js | `Path.quadTo` | 59% | 62% | 63% | 58% | 60% | 60% | 62% |
| Bezier.js | `Bezier.raise` | 68% | 67% | 70% | 64% | 65% | 68% | 72% |
| Snap.svg | `Q path command` | 0 | 0 | 0 | 0 | 0 | 57% | 63% |
| Raphael | `Q path command` | 79% | 79% | 80% | 80% | 78% | 79% | 81% |

## Glyph outlines

**Glyph outlines.** Every quadratic segment of the simple glyphs of DejaVu Sans (48,404 segments, 1,023 of which turn around inside the segment, 2.1%) and DejaVu Sans Oblique (45,475 segments, 3,867 of which turn around inside the segment, 8.5%), in font units, from the files installed with matplotlib 3.11.2. Number of wrong boxes when the segment is stored as a cubic, and when it is passed as a quadratic to the entry points of the previous section.

| Library | DejaVu Sans, as cubics | DejaVu Sans Oblique, as cubics | DejaVu Sans, as quadratics | DejaVu Sans Oblique, as quadratics |
|---|---:|---:|---:|---:|
| Raphael | 229 | 1815 | 226 | 1885 |
| beziers.py | 259 | 2015 |  |  |
| Bezier.js | 59 | 824 | 64 | 826 |
| svg.path | 57 | 834 |  |  |
| opentype.js | 11 | 274 | 19 | 218 |
| PDF.js | 0 | 13 |  |  |
| Snap.svg | 0 | 3 | 0 | 7 |
| Qt | 0 | 3 | 0 | 0 |
| fabric.js | 0 | 3 |  |  |

## Cross-check

Wrong boxes over all families, counted against the exact reference and, independently of it, against points of the curve evaluated in floating point at 257 parameters. Where the library converts a quadratic itself, the points are those of the quadratic.

| Library | Exact reference | Sampled points |
|---|---:|---:|
| svgpathtools | 3614 | 3614 |
| svg.path | 5591 | 5591 |
| svgelements | 1809 | 1809 |
| fontTools | 540 | 540 |
| matplotlib | 0 | 0 |
| beziers.py | 15067 | 15067 |
| inkex | 2 | 2 |
| kurbo | 0 | 0 |
| Skia | 0 | 0 |
| Qt | 3114 | 3114 |
| cairo | 0 | 0 |
| Core Graphics | 0 | 0 |
| fabric.js | 1562 | 1562 |
| opentype.js | 10501 | 10501 |
| Bezier.js | 11245 | 11245 |
| PDF.js | 1270 | 1270 |
| Paper.js | 0 | 0 |
| Two.js | 5606 | 5606 |
| ZRender | 993 | 993 |
| Konva | 0 | 0 |
| AntV G | 3718 | 3718 |
| Snap.svg | 2772 | 2772 |
| Raphael | 15247 | 15247 |
| svg-path-bbox | 1840 | 1840 |
| svg-path-commander | 1840 | 1840 |
| thi.ng/geom-splines | 0 | 0 |
| OpenJDK | 0 | 0 |

## Size of the misses

The distance by which a box fell short of the curve, as a fraction of the curve's extent along that axis, over the four cubic families: the number of wrong boxes, how many of them miss by more than 1% and 10%, and the largest miss.

The last column is the largest distance by which a box extends beyond the curve, which is not counted as wrong.

| Library | Wrong | Over 1% | Over 10% | Largest miss | Largest excess |
|---|---:|---:|---:|---:|---:|
| svgpathtools | 3614 | 3445 | 2863 | 1.0e+00 | 7.8e-05 |
| svg.path | 4700 | 3393 | 1353 | 1.0e+00 | 9.4e-05 |
| svgelements | 1809 | 1760 | 1564 | 1.0e+00 | 1.0e-09 |
| fontTools | 540 | 315 | 45 | 2.4e-01 | 2.6e-05 |
| matplotlib | 0 | 0 | 0 | 3.4e-05 | 9.4e-05 |
| beziers.py | 12793 | 11688 | 9106 | 1.0e+00 | 4.7e-05 |
| inkex | 2 | 2 | 2 | 1.0e+00 | 9.4e-05 |
| kurbo | 0 | 0 | 0 | 5.5e-05 | 2.9e-05 |
| Skia | 0 | 0 | 0 | 0.0e+00 | 0.0e+00 |
| Qt | 1916 | 1452 | 788 | 1.0e+00 | 9.4e-05 |
| cairo | 0 | 0 | 0 | 0.0e+00 | 0.0e+00 |
| Core Graphics | 0 | 0 | 0 | 2.6e-05 | 2.6e-05 |
| fabric.js | 1559 | 1071 | 466 | 1.0e+00 | 1.1e-04 |
| opentype.js | 5731 | 4193 | 2135 | 1.0e+00 | 4.3e-05 |
| Bezier.js | 4747 | 3563 | 1603 | 1.0e+00 | 4.0e-05 |
| PDF.js | 1257 | 814 | 224 | 1.0e+00 | 9.4e-05 |
| Paper.js | 0 | 0 | 0 | 6.0e-05 | 3.1e-05 |
| Two.js | 5606 | 5516 | 5052 | 1.0e+00 | 1.1e-04 |
| ZRender | 993 | 974 | 854 | 1.0e+00 | 1.1e-04 |
| Konva | 0 | 0 | 0 | 1.3e-04 | 1.1e-04 |
| AntV G | 3718 | 3659 | 3311 | 1.0e+00 | 7.7e+02 |
| Snap.svg | 1559 | 1071 | 466 | 1.0e+00 | 1.1e-04 |
| Raphael | 5539 | 3840 | 229 | 1.1e-01 | 9.4e-05 |
| svg-path-bbox | 1840 | 1796 | 1618 | 1.0e+00 | 3.0e-01 |
| svg-path-commander | 1840 | 1796 | 1618 | 1.0e+00 | 3.0e-01 |
| thi.ng/geom-splines | 0 | 0 | 0 | 5.3e-05 | 1.1e-04 |
| OpenJDK | 0 | 0 | 0 | 2.2e-16 | 1.1e-04 |
