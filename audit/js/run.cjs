// Runs one JavaScript library over a batch of curves.
//
//   node run.cjs <library> < curves.json > boxes.json
//   node run.cjs --quadratic <library> < quadratics.json > boxes.json
//   node run.cjs --list
//
// Input: a JSON array of curves, each eight numbers x0, y0, ..., x3, y3
// (six for --quadratic).
// Output: a JSON array with one [xmin, ymin, xmax, ymax] or null per curve,
// or {"error": "..."} if the library could not be loaded.

const path = (c) =>
  `M ${c[0]} ${c[1]} C ${c[2]} ${c[3]} ${c[4]} ${c[5]} ${c[6]} ${c[7]}`;

function dom() {
  const { JSDOM } = require('jsdom');
  const { window } = new JSDOM('<!doctype html><html><body></body></html>');
  global.window = window;
  global.document = window.document;
}

const libraries = {
  'fabric.js': ['fabric', 'util.getBoundsOfCurve', async () => {
    const { util } = await import('fabric');
    return (c) => {
      const [min, max] = util.getBoundsOfCurve(...c);
      return [min.x, min.y, max.x, max.y];
    };
  }],
  'opentype.js': ['opentype.js', 'Path.getBoundingBox', async () => {
    const opentype = require('opentype.js');
    return (c) => {
      const p = new opentype.Path();
      p.moveTo(c[0], c[1]);
      p.curveTo(c[2], c[3], c[4], c[5], c[6], c[7]);
      const b = p.getBoundingBox();
      return [b.x1, b.y1, b.x2, b.y2];
    };
  }],
  'Bezier.js': ['bezier-js', 'Bezier.bbox', async () => {
    const { Bezier } = require('bezier-js');
    return (c) => {
      const b = new Bezier(...c).bbox();
      return [b.x.min, b.y.min, b.x.max, b.y.max];
    };
  }],
  'PDF.js': ['pdfjs-dist', 'Util.bezierBoundingBox', async () => {
    const { Util } = await import('pdfjs-dist/legacy/build/pdf.mjs');
    return (c) => {
      const box = new Float64Array([Infinity, Infinity, -Infinity, -Infinity]);
      Util.bezierBoundingBox(...c, box);
      return Array.from(box);
    };
  }],
  'Paper.js': ['paper', 'Path.bounds', async () => {
    const paper = require('paper/dist/paper-core.js');
    paper.setup(new paper.Size(1, 1));
    return (c) => {
      const b = new paper.Path(path(c)).bounds;
      return [b.left, b.top, b.right, b.bottom];
    };
  }],
  'Two.js': ['two.js', 'getCurveBoundingBox', async () => {
    const { getCurveBoundingBox } = await import('two.js/src/utils/curves.js');
    return (c) => {
      const b = getCurveBoundingBox(...c);
      return [b.min.x, b.min.y, b.max.x, b.max.y];
    };
  }],
  'ZRender': ['zrender', 'bbox.fromCubic', async () => {
    const { fromCubic } = require('zrender/lib/core/bbox.js');
    return (c) => {
      const min = [0, 0];
      const max = [0, 0];
      fromCubic(...c, min, max);
      return [min[0], min[1], max[0], max[1]];
    };
  }],
  'Konva': ['konva', 'Path.getSelfRect', async () => {
    const konva = require('konva');
    const Konva = konva.default || konva;
    return (c) => {
      const r = new Konva.Path({ data: path(c) }).getSelfRect();
      return [r.x, r.y, r.x + r.width, r.y + r.height];
    };
  }],
  'AntV G': ['@antv/g-math', 'cubicBox', async () => {
    const { cubicBox } = require('@antv/g-math');
    return (c) => {
      const b = cubicBox(...c);
      return [b.x, b.y, b.x + b.width, b.y + b.height];
    };
  }],
  'Snap.svg': ['snapsvg', 'Snap.path.getBBox', async () => {
    dom();
    const Snap = require('snapsvg');
    return (c) => {
      const b = Snap.path.getBBox(path(c));
      return [b.x, b.y, b.x2, b.y2];
    };
  }],
  'Raphael': ['raphael', 'Raphael.pathBBox', async () => {
    dom();
    const Raphael = require('raphael');
    return (c) => {
      const b = Raphael.pathBBox(path(c));
      return [b.x, b.y, b.x2, b.y2];
    };
  }],
  'svg-path-bbox': ['svg-path-bbox', 'svgPathBbox', async () => {
    const { svgPathBbox } = require('svg-path-bbox');
    return (c) => svgPathBbox(path(c));
  }],
  'svg-path-commander': ['svg-path-commander', 'getPathBBox', async () => {
    const module = require('svg-path-commander');
    const { getPathBBox } = module.default || module;
    return (c) => {
      const b = getPathBBox(path(c));
      return [b.x, b.y, b.x2, b.y2];
    };
  }],
  'thi.ng/geom-splines': ['@thi.ng/geom-splines', 'cubicBounds', async () => {
    const { cubicBounds } = await import('@thi.ng/geom-splines');
    return (c) => {
      const [min, max] = cubicBounds(
        [c[0], c[1]], [c[2], c[3]], [c[4], c[5]], [c[6], c[7]]);
      return [min[0], min[1], max[0], max[1]];
    };
  }],
};

// Version of an installed package, read from its package.json. Not every
// package exports that file, so it is located on disk.
function installedVersion(pkg) {
  const fs = require('fs');
  const { join, dirname } = require('path');
  for (let dir = __dirname; ; dir = dirname(dir)) {
    const file = join(dir, 'node_modules', pkg, 'package.json');
    if (fs.existsSync(file)) {
      return JSON.parse(fs.readFileSync(file, 'utf8')).version;
    }
    if (dir === dirname(dir)) {
      return null;
    }
  }
}

// Entry points that take a quadratic segment (six numbers) and convert it to
// a cubic internally before computing the box.
const qpath = (q) => `M ${q[0]} ${q[1]} Q ${q[2]} ${q[3]} ${q[4]} ${q[5]}`;
const quadratic = {
  'opentype.js': ['Path.quadTo', async () => {
    const opentype = require('opentype.js');
    return (q) => {
      const p = new opentype.Path();
      p.moveTo(q[0], q[1]);
      p.quadTo(q[2], q[3], q[4], q[5]);
      const b = p.getBoundingBox();
      return [b.x1, b.y1, b.x2, b.y2];
    };
  }],
  'Bezier.js': ['Bezier.raise', async () => {
    const { Bezier } = require('bezier-js');
    return (q) => {
      const b = new Bezier(...q).raise().bbox();
      return [b.x.min, b.y.min, b.x.max, b.y.max];
    };
  }],
  'Snap.svg': ['Q path command', async () => {
    dom();
    const Snap = require('snapsvg');
    return (q) => {
      const b = Snap.path.getBBox(qpath(q));
      return [b.x, b.y, b.x2, b.y2];
    };
  }],
  'Raphael': ['Q path command', async () => {
    dom();
    const Raphael = require('raphael');
    return (q) => {
      const b = Raphael.pathBBox(qpath(q));
      return [b.x, b.y, b.x2, b.y2];
    };
  }],
};

async function main() {
  let name = process.argv[2];
  let table = libraries;
  if (name === '--quadratic') {
    name = process.argv[3];
    table = { [name]: [null, null, quadratic[name][1]] };
  }
  if (name === '--list') {
    const list = {};
    for (const [key, [pkg, entry]] of Object.entries(libraries)) {
      const version = installedVersion(pkg);
      const quadraticEntry = quadratic[key] ? quadratic[key][0] : null;
      list[key] = { package: pkg, entry, version, quadraticEntry };
    }
    return list;
  }
  let box;
  try {
    box = await table[name][2]();
  } catch (e) {
    return { error: String((e && e.message) || e) };
  }
  const curves = JSON.parse(require('fs').readFileSync(0, 'utf8'));
  return curves.map((c) => {
    try {
      const b = Array.from(box(c), Number);
      return b.length === 4 && b.every(Number.isFinite) ? b : null;
    } catch (e) {
      return null;
    }
  });
}

// Some libraries keep timers or handles open; exit once the output is flushed.
main().then((out) => process.stdout.write(JSON.stringify(out), () => process.exit(0)));
