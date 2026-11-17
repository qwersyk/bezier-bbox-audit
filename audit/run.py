"""Run every available library over the corpus and record how often its
bounding box leaves part of the curve outside.

    python -m audit.run            # writes results/results.json
    python -m audit.run --check    # compares the counts with that file instead
"""

import functools
import json
import platform
import subprocess
import sys
import warnings
from fractions import Fraction
from importlib import metadata
from pathlib import Path

from . import corpus, fonts, oracle
from .libraries import LIBRARIES, QUADRATIC

ROOT = Path(__file__).resolve().parent.parent
JS = ROOT / "audit" / "js"
JAVA = ROOT / "audit" / "java" / "Bounds.java"

# A box is counted as wrong when, along either axis, the curve extends beyond
# it by more than this fraction of the curve's extent along that axis.
THRESHOLD = 1e-3

# Wrong boxes are also counted by size of the miss: above each of these
# fractions of the extent.
LEVELS = (1e-2, 1e-1)

# Language of the implementation, where it is not the language of the binding.
NATIVE = {"kurbo": "Rust", "Skia": "C++", "Qt": "C++", "cairo": "C",
          "Core Graphics": "C"}

# Coordinate resolution of libraries that do not compute in double precision,
# as a function of the largest coordinate magnitude. A miss within it is not
# counted. cairo stores coordinates in 24.8 fixed point, Skia in single
# precision.
RESOLUTION = {"cairo": lambda largest: 1 / 256,
              "Skia": lambda largest: largest * 2.0**-20}

# Largest coordinate magnitude a library can represent, where that is below
# the range of the corpus. Curves beyond it are not given to the library.
# cairo's 24.8 fixed point holds 24 bits before the point.
LIMIT = {"cairo": 2.0**23}

# Floating-point results depend on the compiler and the CPU, and a count can
# move by a few curves that sit at the edge of failing. This many per cell are
# accepted when a run is compared with the stored one: for compiled libraries
# always, for the others only where the stored count is not zero.
TOLERANCE = 20

# The family name under which quadratic entry points are reported.
OWN_CONVERSION = "quadratic, converted by the library"

# Segments of real glyph outlines: as cubics, and as quadratics passed to the
# same entry points as OWN_CONVERSION. Their columns are font names.
GLYPHS = "glyphs"
GLYPHS_OWN = "glyphs, converted by the library"


def native_version(name):
    """Version of the native library behind a Python binding, if it differs."""
    if name == "cairo":
        import cairo
        return "cairo " + cairo.cairo_version_string()
    if name == "Core Graphics":
        return "macOS " + platform.mac_ver()[0]
    return None


def python_boxes(factory, curves):
    box = factory()
    out = []
    for curve in curves:
        try:
            b = [float(v) for v in box(curve)]
            finite = all(v == v and abs(v) != float("inf") for v in b)
            out.append(b if len(b) == 4 and finite else None)
        except Exception:
            out.append(None)
    return out


def javascript_boxes(name, curves, quadratic=False):
    command = ["node", "run.cjs"] + (["--quadratic"] if quadratic else []) + [name]
    done = subprocess.run(command, input=json.dumps(curves), capture_output=True,
                          text=True, cwd=JS, timeout=600)
    out = json.loads(done.stdout)
    if isinstance(out, dict):
        raise RuntimeError(out["error"])
    if len(out) != len(curves):
        raise RuntimeError(f"{len(out)} boxes for {len(curves)} curves")
    return out


def java_boxes(curves):
    text = "\n".join(" ".join(repr(v) for v in c) for c in curves) + "\n"
    done = subprocess.run(["java", str(JAVA)], input=text, capture_output=True,
                          text=True, timeout=600, check=True)
    out = [[float(v) for v in line.split()] for line in done.stdout.splitlines()]
    if len(out) != len(curves):
        raise RuntimeError(f"{len(out)} boxes for {len(curves)} curves")
    return out


SAMPLES = 256


@functools.lru_cache(maxsize=None)
def sampled_box(curve):
    """Box of the points of a cubic or quadratic (a tuple of coordinates) at
    SAMPLES + 1 parameters, evaluated in floats. Independent of the exact
    reference."""
    n = len(curve) // 2 - 1
    weights = (1, 3, 3, 1) if n == 3 else (1, 2, 1)
    xs, ys = [], []
    for i in range(SAMPLES + 1):
        t = i / SAMPLES
        w = [weights[k] * t**k * (1 - t)**(n - k) for k in range(n + 1)]
        xs.append(sum(a * b for a, b in zip(w, curve[0::2])))
        ys.append(sum(a * b for a, b in zip(w, curve[1::2])))
    return min(xs), min(ys), max(xs), max(ys)


def deviation(box, reference, resolution=0):
    """How far a box falls short of the reference box and how far it extends
    beyond it, each as a fraction of the reference's extent along the same
    axis, and each reduced by the resolution first. Along an axis of zero
    extent any deviation counts as 1."""
    short = excess = 0.0
    for axis in (0, 1):
        lo, hi = reference[axis], reference[axis + 2]
        low, high = box[axis] - lo, hi - box[axis + 2]
        for gap, sign in ((max(low, high), 1), (max(-low, -high), -1)):
            gap -= resolution
            if gap > 0:
                value = float(gap / (hi - lo)) if hi > lo else 1.0
                if sign > 0:
                    short = max(short, value)
                else:
                    excess = max(excess, value)
    return short, excess


def measure(curves, truth, boxes, resolution=None, limit=None):
    """Summarise one library on one batch."""
    if not len(curves) == len(truth) == len(boxes):
        raise ValueError(f"{len(curves)} curves, {len(truth)} exact boxes, {len(boxes)} boxes")
    wrong = failed = sampled = unsupported = 0
    worst_short = worst_excess = 0.0
    above = [0] * len(LEVELS)
    example = None
    for curve, exact, box in zip(curves, truth, boxes):
        largest = max(abs(v) for v in curve)
        if limit and largest >= limit:
            unsupported += 1
            continue
        if box is None:
            failed += 1
            continue
        allowed = resolution(largest) if resolution else 0
        if deviation(box, sampled_box(tuple(curve)), allowed)[0] > THRESHOLD:
            sampled += 1
        short, excess = deviation([Fraction(v) for v in box], exact, Fraction(allowed))
        if short > THRESHOLD:
            wrong += 1
            above = [n + (short > level) for n, level in zip(above, LEVELS)]
        if short > worst_short:
            worst_short, example = short, curve
        worst_excess = max(worst_excess, excess)
    cell = {"wrong": wrong, "wrong_sampled": sampled, "failed": failed,
            "worst_short": worst_short, "worst_excess": worst_excess}
    if wrong:
        cell["wrong_above"] = above
        cell["example"] = example
    if unsupported:
        cell["unsupported"] = unsupported
    return cell


def cells(batches, truth, boxes, resolution=None, limit=None):
    if not len(truth) == len(boxes) == sum(len(batch) for _, _, batch in batches):
        raise ValueError("the number of boxes does not match the number of curves")
    out, start = {}, 0
    for family, k, batch in batches:
        stop = start + len(batch)
        out.setdefault(family, {})[str(k)] = measure(
            batch, truth[start:stop], boxes[start:stop], resolution, limit)
        start = stop
    return out


def exact_quadratic_box(q):
    """Exact box of a quadratic segment, through its exact cubic form."""
    q = [Fraction(v) for v in q]
    third = Fraction(2, 3)
    cubic = [q[0], q[1],
             q[0] + third * (q[2] - q[0]), q[1] + third * (q[3] - q[1]),
             q[4] + third * (q[2] - q[4]), q[5] + third * (q[3] - q[5]),
             q[4], q[5]]
    return oracle.bbox(cubic)[0]


def compare(stored, fresh, unavailable=()):
    """Report where a fresh run disagrees with the stored one; return the
    number of disagreements. Only counts are compared. A library that did
    not run is a disagreement unless it is listed as unavailable here.
    Counts may differ by TOLERANCE, as described there."""
    if stored["corpus"] != fresh["corpus"]:
        print("the corpus differs from the stored one")
        return 1
    if stored.get("glyphs") != fresh.get("glyphs"):
        print("the glyph outlines differ from the stored ones")
        return 1
    differences = 0
    for name, info in stored["libraries"].items():
        now = fresh["libraries"].get(name)
        if now is None:
            print(f"{name}: not run")
            differences += name not in unavailable
            continue
        note = "" if now["version"] == info["version"] else \
            f" (stored {info['version']}, installed {now['version']})"
        changed = [f"{family}/{k}: {cell['wrong']} wrong, {cell['failed']} failed -> "
                   f"{now['cells'][family][k]['wrong']} wrong, {now['cells'][family][k]['failed']} failed"
                   for family, row in info["cells"].items() for k, cell in row.items()
                   if (cell["wrong"], cell["failed"]) !=
                   (now["cells"][family][k]["wrong"], now["cells"][family][k]["failed"])]
        print(f"{name}{note}: {'same counts' if not changed else '; '.join(changed)}")
        differences += sum(
            cell["failed"] != now["cells"][family][k]["failed"]
            or abs(cell["wrong"] - now["cells"][family][k]["wrong"])
            > (TOLERANCE if name in NATIVE or cell["wrong"] else 0)
            for family, row in info["cells"].items() for k, cell in row.items())
    return differences


def main():
    warnings.filterwarnings("ignore")
    batches = list(corpus.cases())
    q_batches = [(OWN_CONVERSION, k, corpus.quadratics(k)) for k in corpus.RANGES]
    try:
        glyphs, outlines = fonts.load()
    except Exception as error:
        print(f"skipped glyph outlines: {error!r}", file=sys.stderr)
        glyphs, outlines = None, {}
    for font, quadratics in outlines.items():
        batches.append((GLYPHS, font, [corpus.raise_degree(q) for q in quadratics]))
        q_batches.append((GLYPHS_OWN, font, quadratics))
    example = corpus.raise_degree(corpus.EXAMPLE)
    curves = [c for _, _, batch in batches for c in batch] + [example]
    truth = [oracle.bbox(c)[0] for c in curves]
    example_boxes = {}

    q_curves = [q for _, _, batch in q_batches for q in batch]
    q_truth = [exact_quadratic_box(q) for q in q_curves]

    libraries = {}

    def record(name, info, boxes, q_entry=None, q_boxes=None):
        resolution, limit = RESOLUTION.get(name), LIMIT.get(name)
        example_boxes[name] = boxes[-1]
        info["cells"] = cells(batches, truth[:-1], boxes[:-1], resolution, limit)
        if q_boxes is not None:
            info["quadratic_entry"] = q_entry
            info["cells"].update(cells(q_batches, q_truth, q_boxes, resolution, limit))
        libraries[name] = info

    for name, (distribution, entry, factory) in LIBRARIES.items():
        try:
            info = {"language": NATIVE.get(name, "Python"), "package": distribution,
                    "version": metadata.version(distribution), "entry": entry}
            if native_version(name):
                info["native"] = native_version(name)
            boxes = python_boxes(factory, curves)
            q_entry, q_boxes = None, None
            if name in QUADRATIC:
                q_entry, q_factory = QUADRATIC[name]
                q_boxes = python_boxes(q_factory, q_curves)
        except Exception as error:
            print(f"skipped {name}: {error!r}", file=sys.stderr)
            continue
        record(name, info, boxes, q_entry, q_boxes)

    try:
        listing = json.loads(subprocess.run(
            ["node", "run.cjs", "--list"], capture_output=True, text=True,
            cwd=JS, check=True).stdout)
    except Exception as error:
        print(f"skipped JavaScript: {error!r}", file=sys.stderr)
        listing = {}
    for name, item in listing.items():
        try:
            boxes = javascript_boxes(name, curves)
            q_entry, q_boxes = item["quadraticEntry"], None
            if q_entry:
                q_boxes = javascript_boxes(name, q_curves, quadratic=True)
        except Exception as error:
            print(f"skipped {name}: {error!r}", file=sys.stderr)
            continue
        info = {"language": "JavaScript", "package": item["package"],
                "version": item["version"].lstrip("v"), "entry": item["entry"]}
        record(name, info, boxes, q_entry, q_boxes)

    try:
        version = subprocess.run(["java", str(JAVA), "--version"], capture_output=True,
                                 text=True, check=True).stdout.strip()
        record("OpenJDK", {"language": "Java", "package": "java.desktop",
                           "version": version, "entry": "CubicCurve2D.getBounds2D"},
               java_boxes(curves))
    except Exception as error:
        print(f"skipped OpenJDK: {error!r}", file=sys.stderr)

    node = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()
    results = {
        "corpus": {"seed": corpus.SEED, "sha256": corpus.digest(),
                   "families": list(corpus.FAMILIES) + [OWN_CONVERSION],
                   "ranges": list(corpus.RANGES), "offsets": list(corpus.OFFSETS),
                   "curves_per_cell": corpus.COUNT},
        "threshold": THRESHOLD,
        "levels": list(LEVELS),
        **({"glyphs": glyphs} if glyphs else {}),
        "environment": {"python": platform.python_version(), "node": node,
                        "platform": platform.platform()},
        "example": {"quadratic": corpus.EXAMPLE, "cubic": example,
                    "exact": [float(v) for v in truth[-1]], "boxes": example_boxes},
        "libraries": libraries,
    }
    out = ROOT / "results" / "results.json"
    if "--check" in sys.argv[1:]:
        unavailable = () if platform.system() == "Darwin" else ("Core Graphics",)
        sys.exit(compare(json.loads(out.read_text()), results, unavailable))
    out.write_text(json.dumps(results, indent=1) + "\n")
    print(f"wrote {out.relative_to(ROOT)}: {len(libraries)} libraries, "
          f"{len(curves) - 1} cubics, {len(q_curves)} quadratics")


if __name__ == "__main__":
    main()
