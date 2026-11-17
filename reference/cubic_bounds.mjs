// Bounding box of a cubic Bezier segment in ordinary floating point.
// See cubic_bounds.py for the derivation; the two files perform the same
// operations in the same order and return identical results.

/** Minimum and maximum over 0 <= t <= 1 of the cubic Bezier polynomial
 *  with control values p0, p1, p2, p3. */
export function cubicRange(p0, p1, p2, p3) {
  const d0 = p1 - p0;
  const d1 = p2 - p1;
  const d2 = p3 - p2;
  const a = d0 - 2 * d1 + d2;
  const h = d1 - d0;
  const c = d0;
  let lo = Math.min(p0, p3);
  let hi = Math.max(p0, p3);
  const scale = Math.max(Math.abs(a), Math.abs(h), Math.abs(c));
  if (scale === 0) {
    return [lo, hi];
  }
  // The roots do not depend on a common factor; dividing it out keeps the
  // squares below from overflowing or underflowing.
  const sa = a / scale;
  const sh = h / scale;
  const sc = c / scale;
  const disc = sh * sh - sa * sc;
  if (disc >= 0) {
    const root = Math.sqrt(disc);
    const q = -(sh + (sh < 0 || Object.is(sh, -0) ? -root : root));
    for (const [numerator, denominator] of [[q, sa], [sc, q]]) {
      if (denominator !== 0) {
        const t = numerator / denominator;
        if (t > 0 && t < 1) {
          // de Casteljau: every step is a weighted mean, so nothing overflows.
          const s = 1 - t;
          const q0 = s * p0 + t * p1;
          const q1 = s * p1 + t * p2;
          const q2 = s * p2 + t * p3;
          const value = s * (s * q0 + t * q1) + t * (s * q1 + t * q2);
          lo = Math.min(lo, value);
          hi = Math.max(hi, value);
        }
      }
    }
  }
  return [lo, hi];
}

/** Bounding box [xmin, ymin, xmax, ymax] of a cubic Bezier segment. */
export function cubicBounds(x0, y0, x1, y1, x2, y2, x3, y3) {
  const [xmin, xmax] = cubicRange(x0, x1, x2, x3);
  const [ymin, ymax] = cubicRange(y0, y1, y2, y3);
  return [xmin, ymin, xmax, ymax];
}
