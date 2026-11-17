# Cancellation in cubic Bézier bounding boxes

## 1. The computation

One coordinate of a cubic Bézier segment with control values $p_0, p_1, p_2, p_3$ is

$$B(t) = p_0 + 3 d_0 t + 3 (d_1 - d_0) t^2 + (d_0 - 2 d_1 + d_2) t^3, \qquad d_i = p_{i+1} - p_i .$$

Its range over $0 \le t \le 1$ is attained at the end points or where $B'(t) = 0$:

$$a t^2 + 2 h t + c = 0, \qquad a = d_0 - 2 d_1 + d_2, \quad h = d_1 - d_0, \quad c = d_0 .$$

The bounding box of a segment is this range for $x$ and for $y$.

## 2. Where it goes wrong

The textbook roots are

$$t_\pm = \frac{-h \pm \sqrt{h^2 - a c}}{a} .$$

Suppose $|a c| \ll h^2$. Then $\sqrt{h^2 - ac} \approx |h|$ and one of the two numerators is a difference of nearly equal quantities. Its exact value is about $-ac/2h$, while the rounding error already present in the square root is about $u|h|$, with $u = 2^{-53}$. The computed root therefore carries an absolute error of order

$$\delta t \approx \frac{u\,|h|}{|a|} .$$

This is the root that stays finite as $a \to 0$, the one that matters. The other root, of magnitude $2|h/a|$, is computed accurately and is outside $[0, 1]$.

A small error in a stationary parameter is harmless, because the curve is flat there: the value changes by about $\tfrac12 |B''| \delta t^2$. The damage is done when $\delta t$ is of order one, so that the computed root leaves $(0, 1)$ and is discarded, or lands at an unrelated parameter.

That happens exactly when $a$ is itself rounding error. A quadratic segment $q_0, q_1, q_2$ written as a cubic has $p_1 = q_0 + \tfrac23 (q_1 - q_0)$, $p_2 = q_2 + \tfrac23 (q_1 - q_2)$ and $a = 0$. Evaluated in floating point, $p_1$ and $p_2$ are rounded and $a$ comes out as a few units of $uM$, where $M$ is the magnitude of the coordinates. Then $\delta t \approx |h| / M$, which is of order one whenever the curve is not small compared with its coordinates. The same can happen for any cubic whose leading coefficient cancels, such as a mirror-symmetric arch $(p, r, r, p)$; whether it does depends on the order in which an implementation adds the terms of $a$.

## 3. Why fixed tolerances do not help

Most implementations test for the degenerate case before using the formula, and fall back to the linear equation $2ht + c = 0$ when the test succeeds.

**Exact test, `a == 0`.** The computed $a$ is rounding error, not zero, so the test never fires for a converted quadratic. These implementations fail at every scale.

**Fixed tolerance, too small.** The rounding error in $a$ is a few $uM \approx 10^{-16} M$. It stays below $10^{-12}$ for coordinates up to a few thousand and exceeds it beyond, so an implementation with `abs(a) < 1e-12` starts failing between $M = 10^2$ and $10^4$. With a tolerance of $10^{-10}$ the onset moves up by two orders of magnitude. Both match the measured tables.

**Fixed tolerance, too large.** The coefficients scale with the coordinates. When the coordinates are small enough, $a$ of an ordinary cubic falls below the tolerance, the curve is treated as a quadratic or as a line, and its extrema are computed for the wrong polynomial or not at all. With `abs(a) < 0.001` this happens for coordinates around $10^{-4}$, and proportionally lower for smaller tolerances. The corpus reaches down to $10^{-6}$ and therefore shows only the largest ones.

A fixed tolerance is thus wrong at both ends, and the usable range between them shrinks as it is made safer at one. A tolerance relative to $|h|$ would work, but none is needed.

**Expanded discriminant.** A separate problem affects implementations that write the discriminant as a polynomial in the control values, $p_1^2 - (p_0 + p_1) p_2 + p_2^2 + (p_0 - p_1) p_3$. Its terms are of order $M^2$ while its value is of the order of the squared size of the curve. For a curve of size $s$ at distance $M$ from the origin the result is rounding error once $s^2 \lesssim u M^2$, that is $s / M \lesssim 10^{-8}$. Forming $h^2 - ac$ from the differences $d_i$ avoids this.

## 4. Stable evaluation

Let

$$q = -\bigl(h + \operatorname{sign}(h)\sqrt{h^2 - a c}\bigr) .$$

The two terms have the same sign, so nothing cancels. The roots are

$$t_1 = \frac{q}{a}, \qquad t_2 = \frac{c}{q},$$

the second from the product of the roots, $t_1 t_2 = c/a$. This is the standard remedy [1, 2]. For $a = 0$ it gives $t_2 = -c/2h$, the root of the linear equation, without a separate branch; for $a$ equal to rounding error, $t_1$ is huge and discarded and $t_2$ is accurate. The only comparison with zero is the one that prevents a division by zero.

`reference/cubic_bounds.py` adds three details. The coefficients are divided by their largest magnitude before the discriminant is formed, so that the squares cannot overflow or underflow. The coefficients are built from the differences $d_i$ rather than from the $p_i$, which keeps them accurate for a curve that is small compared with its distance from the origin. And the curve is evaluated at a root by de Casteljau's algorithm, whose steps are weighted means and cannot overflow.

Over the corpus and five further families (coordinates near $10^{-300}$ and $10^{300}$, small integers, mixed magnitudes, thin curves) its error against the exact reference stays within 16 units in the last place of the largest coordinate, which the tests assert. The result is not rounded outward, and the bound is a measurement, not a proof.

## 5. Affected implementations

Leading coefficient equal to rounding error (section 2):

| Library | Routine | Degenerate-case test |
|---|---|---|
| svg.path 7.1 | `_find_solutions_for_bezier`, `svg/path/path.py:20` | `c2 == 0` |
| opentype.js 2.0.0 | `BoundingBox.addBezier`, `dist/opentype.js:327` | `a === 0` |
| Bezier.js 6.1.4 | `utils.droots`, `src/utils.js:626` | `d !== 0` |
| beziers.py 0.6.0 | `quadraticRoots`, `beziers/utils/__init__.py:14` | `a != 0.0` |
| Raphael 2.3.0 | `curveDim`, `raphael.js:2060` | none |
| Qt 6.12 | `qt_painterpath_bezier_extrema`, `src/gui/painting/qpainterpath.cpp` | `qFuzzyIsNull(ax)`, that is `abs(ax) <= 1e-12` |
| PDF.js 6.5.438 | `Util.#getExtremum`, `legacy/build/pdf.mjs:6750` | `Math.abs(a) < 1e-12` |
| fabric.js 7.4.0 | `getBoundsOfCurve`, `src/util/path/index.ts:259` | `abs(a) < 1e-12` |
| Snap.svg 0.5.1 | `curveDim`, `dist/snap.svg.js:6442` | `abs(a) < 1e-12` |
| svgpathtools 1.8.0 | `bezier_real_minmax`, `svgpathtools/bezier.py:175` | `abs(denom) > FLOAT_EPSILON` (1e-12) |
| fontTools 4.68.0 | `solveQuadratic`, `fontTools/misc/bezierTools.py:836` | `abs(a) < epsilon` (1e-10) |

Tolerance too large for small coordinates (section 3):

| Library | Routine | Test |
|---|---|---|
| Two.js 0.8.24 | `getCurveBoundingBox`, `src/utils/curves.js:233` | `Math.abs(a) < 0.001`, then `Math.abs(b) < 0.001` |
| AntV G, @antv/g-math 3.1.0 | `extrema`, `dist/index.js:363` | `isNumberEqual(a, 0)` and `isNumberEqual(disc, 0)`, tolerance 1e-5 |
| ZRender 6.1.0 | `cubicExtrema`, `lib/core/curve.js:117` | `isAroundZero(disc)`, tolerance 1e-8 |

svg-path-bbox and svg-path-commander (`abs(K) < 1e-8`) and inkex (`atol = 1e-9`) show the first few such failures at the smallest coordinates in the corpus.

Expanded discriminant (section 3):

| Library | Routine |
|---|---|
| svgpathtools 1.8.0 | `bezier_real_minmax`, `svgpathtools/bezier.py` |
| svgelements 1.9.6 | `CubicBezier._real_minmax`, `svgelements/svgelements.py`, credited to svgpathtools |
| svg-path-bbox 2.1.0 | `minmaxC`, `dist/index.js:35` |
| svg-path-commander 2.3.5 | `minmaxC`, `dist/index.js:365`, the same expression |

Paths are relative to the installed package at the tested version. The Qt routine was read on the `dev` branch at commit `7ec87c1`; the tested binary is 6.12.0. Every tested package was the latest release on PyPI or npm on 2026-11-17. For the eleven libraries of the first table the test and formula were unchanged on each project's default branch that day; the others were not checked.

Notes:

- fabric.js, Snap.svg and Two.js contain the same routine with different tolerances; the fabric.js source gives its origin as an uncredited code snippet. The PDF.js source cites Snap.svg as the origin of its routine.
- Raphael replaces a root larger than $10^{12}$ in magnitude by $t = 0.5$.
- beziers.py has no linear branch, so an exactly zero leading coefficient yields no stationary points at all; this is why it fails on every symmetric arch. It also discards stationary parameters outside $[0.01, 0.99]$.
- In ZRender the branch taken for a near-zero discriminant stores a root without counting it, so the curve is left with no stationary points.
- In AntV G the same branch accepts a root without checking that it lies in $[0, 1]$, which is how its boxes become too large.
- Qt, opentype.js, Bezier.js, Snap.svg and Raphael convert quadratics to cubics themselves (`quadTo`, `Path.quadTo`, `Bezier.raise`, the `Q` path command) and then compute the box of the cubic, so the first failure is reachable with quadratic input alone.

Of the implementations without wrong boxes, the source was read for two: Skia [3] and Paper.js (`Numerical.solveQuadratic`) both use the stable form of section 4.

## 6. Method

**Reference.** `audit/oracle.py` converts the control points to rationals without rounding and works in exact arithmetic. The square root of the discriminant is bracketed between integers to at least $2^{-256}$ and carried as an interval, refined until every stationary parameter in $[0, 1]$ is known to $2^{-200}$. The bounds it returns are values the curve attains; the true bound differs from them by at most the bracket width times the largest slope.

**Corpus.** Four families of 1000 curves per column. Three are drawn from the square $[0, 10^k]^2$ for $k = -6, -4, \dots, 6$: random cubics; random quadratics converted to cubics in floating point; and mirror-symmetric arches with coordinates of eight significant decimal digits. The fourth consists of random cubics from the unit square moved by $10^k$ along both axes, $k = 0, 2, \dots, 10$. The quadratics are also passed unconverted to the entry points listed above. The generator is seeded and the corpus hash is stored with the results.

**Glyph outlines.** In addition, every quadratic segment of the simple glyphs of DejaVu Sans and DejaVu Sans Oblique is tested in font units, as a cubic and through the same entry points. The fonts are read from the files that matplotlib installs; runs of off-curve points are split at the implied on-curve points.

**Why random cubics pass at ordinary coordinates.** For a random cubic $a$ is of the order of the coordinates and nothing cancels. For a converted quadratic the computed $a$ is rounding error and is rarely exactly zero: evaluated as $-p_0 + 3p_1 - 3p_2 + p_3$, it is nonzero in $x$ or $y$ for 915 of the 1000 quadratics at range $[0, 1]$. This is why an exact test for zero fails most of the time.

**Criterion.** A box is wrong when, along either axis, the curve extends beyond it by more than $10^{-3}$ of the curve's extent along that axis. Measuring each axis against its own extent matters for thin curves, where losing the whole short side is a small fraction of the long one. Misses within a library's coordinate resolution are not counted: $1/256$ for cairo, which stores 24.8 fixed point, and $2^{-20}$ of the largest coordinate for Skia, which computes in single precision. Boxes that are too large are recorded separately and not counted as wrong.

**Cross-check.** Each box is also compared with points of the curve evaluated in floating point at 257 parameters, without the exact reference; for the quadratic entry points these are points of the original quadratic. The totals are the same for every library.

## 7. Limitations

Apart from the two fonts, the corpus is synthetic and its failure rates are properties of the corpus. Only single segments with finite coordinates are tested, at one version of each library. The analysis in sections 2 and 3 is a first-order estimate. Whether a wrong box has a visible effect in an application was not examined. The reference implementation requires that differences of the control values, and four times those differences, do not overflow.

## References

1. W. H. Press, S. A. Teukolsky, W. T. Vetterling, B. P. Flannery. *Numerical Recipes*, 3rd ed., Cambridge University Press, 2007, §5.6.
2. D. Goldberg. What Every Computer Scientist Should Know About Floating-Point Arithmetic. *ACM Computing Surveys* 23(1), 1991. https://doi.org/10.1145/103162.103163
3. Skia, `SkFindUnitQuadRoots`, `src/core/SkGeometry.cpp`. https://github.com/google/skia/blob/main/src/core/SkGeometry.cpp
4. OpenJDK, JDK-8176501, "Method Shape.getBounds2D() incorrectly includes Bezier control points in bounding box". https://bugs.openjdk.org/browse/JDK-8176501
