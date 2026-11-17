"""Draw docs/example.svg from the example recorded in results/results.json.

    python -m audit.figure
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PANELS = ("exact", "Qt", "PDF.js", "fabric.js", "Bezier.js", "fontTools")
WIDTH, HEIGHT, MARGIN, LABEL = 200, 180, 16, 26

STYLE = """
  text { font: 13px -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; fill: #57606a; }
  .curve { fill: none; stroke: #24292f; stroke-width: 1.6; stroke-linecap: round; }
  .box { fill: #0969da; fill-opacity: 0.10; stroke: #0969da; stroke-width: 1.2; }
  .wrong { fill: #cf222e; fill-opacity: 0.10; stroke: #cf222e; }
  @media (prefers-color-scheme: dark) {
    text { fill: #8b949e; }
    .curve { stroke: #e6edf3; }
    .box { fill: #58a6ff; stroke: #58a6ff; }
    .wrong { fill: #f85149; stroke: #f85149; }
  }
"""


def main():
    results = json.loads((ROOT / "results" / "results.json").read_text())
    example = results["example"]
    x0, y0, x1, y1, x2, y2 = example["quadratic"]
    exact = example["exact"]
    scale = min((WIDTH - 2 * MARGIN) / (exact[2] - exact[0]),
                (HEIGHT - 2 * MARGIN) / (exact[3] - exact[1]))

    left = (WIDTH - (exact[2] - exact[0]) * scale) / 2
    top = (HEIGHT - (exact[3] - exact[1]) * scale) / 2

    def place(x, y):
        return (left + (x - exact[0]) * scale, top + (y - exact[1]) * scale)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {3 * WIDTH} {2 * (HEIGHT + LABEL)}" '
           f'width="{3 * WIDTH}" height="{2 * (HEIGHT + LABEL)}" role="img" '
           'aria-label="One curve with its exact bounding box and the boxes returned by five libraries">',
           f"<style>{STYLE}</style>"]
    for index, name in enumerate(PANELS):
        box = exact if name == "exact" else example["boxes"][name]
        version = "" if name == "exact" else " " + results["libraries"][name]["version"]
        (ax, ay), (bx, by) = place(box[0], box[1]), place(box[2], box[3])
        (px, py), (cx, cy), (qx, qy) = place(x0, y0), place(x1, y1), place(x2, y2)
        kind = "box" if name == "exact" else "box wrong"
        out += [
            f'<g transform="translate({index % 3 * WIDTH} {index // 3 * (HEIGHT + LABEL)})">',
            f'<rect class="{kind}" x="{ax:.1f}" y="{ay:.1f}" width="{bx - ax:.1f}" height="{by - ay:.1f}"/>',
            f'<path class="curve" d="M {px:.1f} {py:.1f} Q {cx:.1f} {cy:.1f} {qx:.1f} {qy:.1f}"/>',
            f'<text x="{WIDTH / 2}" y="{HEIGHT + 12}" text-anchor="middle">{name}{version}</text>',
            "</g>",
        ]
    out.append("</svg>")
    (ROOT / "docs" / "example.svg").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
