"""Render results/results.json as Markdown.

    python -m audit.report

Writes results/RESULTS.md and refreshes the tables between the
`<!-- results -->` markers in README.md.
"""

import json
import re
from pathlib import Path

from .run import GLYPHS, GLYPHS_OWN, deviation

ROOT = Path(__file__).resolve().parent.parent
START, END = "<!-- results:start -->", "<!-- results:end -->"


def percent(cell, count):
    if cell.get("unsupported") == count:
        return "n/a"
    share = 100 * cell["wrong"] / count
    text = "0" if share == 0 else f"{share:.1f}%" if share < 10 else f"{share:.0f}%"
    return f"{text}, {cell['failed']} failed" if cell["failed"] else text


def tested(info):
    text = f"{info['package']} {info['version']}"
    return f"{text} ({info['native']})" if "native" in info else text


def header(exponents):
    superscript = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return " | ".join("1" if k == 0 else "10" + str(k).translate(superscript)
                      for k in exponents)


def table(results, family, names, entry_key="entry"):
    """Rows of one family. Columns are powers of ten: the distance from the
    origin for the offset family, the coordinate range for the others."""
    exponents = results["corpus"]["offsets" if family == "offset" else "ranges"]
    count = results["corpus"]["curves_per_cell"]
    lines = [f"| Library | Entry point | {header(exponents)} |",
             "|---|---|" + "---:|" * len(exponents)]
    for name in names:
        info = results["libraries"][name]
        row = " | ".join(percent(info["cells"][family][str(k)], count) for k in exponents)
        lines.append(f"| {name} | `{info[entry_key]}` | {row} |")
    return "\n".join(lines)


def glyphs(results, entries="the table above"):
    """Wrong boxes among the segments of real glyph outlines, as counts.
    `entries` says where the quadratic entry points are listed."""
    described, libraries = results["glyphs"], results["libraries"]
    families = (GLYPHS, GLYPHS_OWN)
    names = sorted((n for n in libraries if wrong_total(libraries[n], families)),
                   key=lambda n: -wrong_total(libraries[n], families))

    def count(cells, family, font):
        if family not in cells:
            return ""
        cell = cells[family][font]
        return f"{cell['wrong']}, {cell['failed']} failed" if cell["failed"] else str(cell["wrong"])

    fonts = [f"{name} ({font['segments']:,} segments, {font['turning']:,} of which turn "
             f"around inside the segment, {100 * font['turning'] / font['segments']:.1f}%)"
             for name, font in described["fonts"].items()]
    columns = [(family, font) for family in families for font in described["fonts"]]
    lines = [
        f"**Glyph outlines.** Every quadratic segment of the simple glyphs of "
        f"{' and '.join(fonts)}, in font units, from the files installed with "
        f"{described['source']}. Number of wrong boxes when the segment is stored as a "
        "cubic, and when it is passed as a quadratic to the entry points of "
        f"{entries}.",
        "",
        "| Library | " + " | ".join(f"{font}, as {'cubics' if family == GLYPHS else 'quadratics'}"
                                   for family, font in columns) + " |",
        "|---|" + "---:|" * len(columns),
    ]
    for name in names:
        cells = libraries[name]["cells"]
        lines.append(f"| {name} | " + " | ".join(count(cells, *column) for column in columns) + " |")
    return lines


def wrong_total(info, families):
    return sum(cell["wrong"] + cell["failed"] for family in families
               for cell in info["cells"].get(family, {}).values())


def sizes(infos, families, levels):
    """Wrong boxes in the given families: their number, and how many of them
    miss the curve by more than each level."""
    found = [cell for info in infos for family in families
             for cell in info["cells"].get(family, {}).values() if cell["wrong"]]
    return (sum(cell["wrong"] for cell in found),
            [sum(cell["wrong_above"][n] for cell in found) for n in range(len(levels))])


def box_text(values):
    return "(" + ", ".join(f"{v:.2f}".rstrip("0").rstrip(".") for v in values) + ")"


def summary(results):
    """The tables shown in the README."""
    libraries = results["libraries"]
    general, quadratic, symmetric, offset, own = results["corpus"]["families"]

    def failing(*families):
        return sorted((n for n in libraries if wrong_total(libraries[n], families)),
                      key=lambda n: -wrong_total(libraries[n], families))

    affected = failing(general, quadratic, symmetric, offset)
    clean = [n for n in libraries if n not in affected]
    elsewhere = [n for n in affected if n not in failing(general, quadratic, offset)]
    count = results["corpus"]["curves_per_cell"]
    example = results["example"]
    exact = example["exact"]
    shown = [n for n in failing(quadratic)
             if deviation(example["boxes"][n], exact)[0] > results["threshold"]]
    total, above = sizes(libraries.values(), (general, quadratic, symmetric, offset),
                         results["levels"])
    small, large = (f"{100 * n / total:.0f}%" for n in above)
    low, high = (f"{level:.0%}" for level in results["levels"])
    return "\n".join([
        "Boxes returned for the curve in the figure, as (xmin, ymin, xmax, ymax):",
        "",
        "| | Box |",
        "|---|---|",
        f"| exact | {box_text(exact)} |",
        *[f"| {name} | {box_text(example['boxes'][name])} |" for name in shown],
        "",
        "## Results",
        "",
        f"Share of wrong boxes among {count} curves per cell. A box is wrong when, along "
        "either axis, the curve extends beyond it by more than 0.1% of its extent along "
        "that axis. Libraries that are not listed in a table have no wrong boxes there.",
        "",
        f"Of the {total:,} wrong boxes for cubic input, {small} miss the curve by more "
        f"than {low} of its extent and {large} by more than {high}; "
        "[results/RESULTS.md](results/RESULTS.md) has the numbers per library.",
        "",
        "**Quadratic segments stored as cubics.** Columns: coordinates drawn from 0 to "
        "the given value.",
        "",
        table(results, quadratic, failing(quadratic)),
        "",
        "**The same quadratics, passed to entry points that convert them to cubics "
        "internally.**",
        "",
        table(results, own, failing(own), "quadratic_entry"),
        "",
        *([*glyphs(results), ""] if "glyphs" in results else []),
        "**Random cubics.** Columns: coordinates drawn from 0 to the given value.",
        "",
        table(results, general, failing(general)),
        "",
        "**Random cubics from the unit square, moved away from the origin.** Columns: "
        "the distance moved along each axis.",
        "",
        table(results, offset, failing(offset)),
        "",
        *([f"Wrong boxes only among the symmetric arches, which are tabulated in "
           f"[results/RESULTS.md](results/RESULTS.md): {', '.join(elsewhere)}.", ""]
          if elsewhere else []),
        f"No wrong boxes anywhere in the corpus: {', '.join(clean)}.",
    ])


def full(results):
    libraries = results["libraries"]
    corpus, env = results["corpus"], results["environment"]
    lines = [
        "# Results",
        "",
        f"Corpus seed {corpus['seed']}, SHA-256 `{corpus['sha256']}`, "
        f"{corpus['curves_per_cell']} curves per cell. A box is wrong when, along either "
        f"axis, the curve extends beyond it by more than {results['threshold']:g} of its "
        "extent along that axis. Columns are the upper end of the coordinate range, or "
        f"for the offset family the distance from the origin. Python {env['python']}, Node "
        f"{env['node'].lstrip('v')}, {env['platform']}.",
        "",
        "## Versions",
        "",
        "| Library | Implementation | Tested through |",
        "|---|---|---|",
    ]
    for name, info in libraries.items():
        lines.append(f"| {name} | {info['language']} | {tested(info)} |")
    for family in corpus["families"]:
        names = [n for n in libraries if family in libraries[n]["cells"]]
        key = "entry" if family in corpus["families"][:4] else "quadratic_entry"
        lines += ["", f"## {family[0].upper()}{family[1:]}", "", table(results, family, names, key)]
    if "glyphs" in results:
        lines += ["", "## Glyph outlines", "", *glyphs(results, "the previous section")]
    lines += ["", "## Cross-check", "",
              "Wrong boxes over all families, counted against the exact reference and, "
              "independently of it, against points of the curve evaluated in floating "
              "point at 257 parameters. Where the library converts a quadratic itself, "
              "the points are those of the quadratic.", "",
              "| Library | Exact reference | Sampled points |", "|---|---:|---:|"]
    for name, info in libraries.items():
        cells = [cell for family in info["cells"].values() for cell in family.values()]
        lines.append(f"| {name} | {sum(c['wrong'] for c in cells)} "
                     f"| {sum(c['wrong_sampled'] for c in cells)} |")
    levels = results["levels"]
    lines += ["", "## Size of the misses", "",
              "The distance by which a box fell short of the curve, as a fraction of "
              "the curve's extent along that axis, over the four cubic families: the "
              "number of wrong boxes, how many of them miss by more than "
              f"{' and '.join(f'{level:.0%}' for level in levels)}, and the largest miss.",
              "",
              "The last column is the largest distance by which a box extends beyond "
              "the curve, which is not counted as wrong.", "",
              "| Library | Wrong | " + " | ".join(f"Over {level:.0%}" for level in levels)
              + " | Largest miss | Largest excess |",
              "|---|" + "---:|" * (len(levels) + 3)]
    for name, info in libraries.items():
        total, above = sizes([info], corpus["families"][:4], levels)
        worst = max(cell["worst_short"] for family in corpus["families"][:4]
                    for cell in info["cells"][family].values())
        excess = max(cell["worst_excess"] for family in corpus["families"][:4]
                     for cell in info["cells"][family].values())
        lines.append(f"| {name} | {total} | " + " | ".join(map(str, above))
                     + f" | {worst:.1e} | {excess:.1e} |")
    return "\n".join(lines) + "\n"


def main():
    results = json.loads((ROOT / "results" / "results.json").read_text())
    (ROOT / "results" / "RESULTS.md").write_text(full(results))
    readme = ROOT / "README.md"
    text = readme.read_text()
    block = f"{START}\n{summary(results)}\n{END}"
    text, found = re.subn(f"{re.escape(START)}.*?{re.escape(END)}",
                          lambda _: block, text, flags=re.S)
    if not found:
        raise SystemExit("README.md has no results markers")
    readme.write_text(text)


if __name__ == "__main__":
    main()
