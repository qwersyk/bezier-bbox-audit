// Smallest reproductions for the JavaScript libraries.
//
//   npm ci && node repro/javascript.mjs
//
// Every case uses the quadratic segment (300000, 600000) (900000, 0)
// (400000, 200000). Its rightmost point is at t = 6/11, x = 6900000/11 =
// 627272.73; its lowest point is at t = 3/4, y = 150000. The exact box is
// therefore (300000, 150000, 627272.73, 600000).

import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const Q = [300000, 600000, 900000, 0, 400000, 200000];
const EXACT = [300000, 150000, 6900000 / 11, 600000];
const D = `M ${Q[0]} ${Q[1]} Q ${Q[2]} ${Q[3]} ${Q[4]} ${Q[5]}`;

// The cubic a converter stores for the quadratic q.
const asCubic = ([x0, y0, x1, y1, x2, y2]) => [
  x0, y0,
  x0 + 2 / 3 * (x1 - x0), y0 + 2 / 3 * (y1 - y0),
  x2 + 2 / 3 * (x1 - x2), y2 + 2 / 3 * (y1 - y2),
  x2, y2];

function dom() {
  const { JSDOM } = require('jsdom');
  const { window } = new JSDOM('<!doctype html><html><body></body></html>');
  globalThis.window = window;
  globalThis.document = window.document;
}

const cases = {
  'fabric.js  util.getBoundsOfCurve': async () => {
    const { util } = await import('fabric');
    const [min, max] = util.getBoundsOfCurve(...asCubic(Q));
    return [min.x, min.y, max.x, max.y];
  },
  'opentype.js  Path.quadTo + getBoundingBox': async () => {
    const opentype = require('opentype.js');
    const p = new opentype.Path();
    p.moveTo(Q[0], Q[1]);
    p.quadTo(Q[2], Q[3], Q[4], Q[5]);
    const b = p.getBoundingBox();
    return [b.x1, b.y1, b.x2, b.y2];
  },
  'Bezier.js  Bezier.raise + bbox': async () => {
    const { Bezier } = require('bezier-js');
    const b = new Bezier(...Q).raise().bbox();
    return [b.x.min, b.y.min, b.x.max, b.y.max];
  },
  'PDF.js  Util.bezierBoundingBox': async () => {
    const { Util } = await import('pdfjs-dist/legacy/build/pdf.mjs');
    const box = new Float64Array([Infinity, Infinity, -Infinity, -Infinity]);
    Util.bezierBoundingBox(...asCubic(Q), box);
    return Array.from(box);
  },
  'Snap.svg  Snap.path.getBBox, Q command': async () => {
    dom();
    const b = require('snapsvg').path.getBBox(D);
    return [b.x, b.y, b.x2, b.y2];
  },
  'Raphael  Raphael.pathBBox, Q command': async () => {
    dom();
    const b = require('raphael').pathBBox(D);
    return [b.x, b.y, b.x2, b.y2];
  },
};

console.log('exact', JSON.stringify(EXACT));
for (const [name, box] of Object.entries(cases)) {
  const got = await box();
  const miss = Math.max(got[0] - EXACT[0], got[1] - EXACT[1], EXACT[2] - got[2], EXACT[3] - got[3]);
  console.log(`${name}\n  ${JSON.stringify(got)}\n  the curve leaves the box by ${miss.toFixed(0)}`);
}
process.exit(0);
