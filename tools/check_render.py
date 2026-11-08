"""Catch the two rendering failures a clean build does not report (vendored from the living-paper skill).

    python3 tools/check_render.py SOURCES... [--brief PDF] [--max-pages 2]

1. Glyphs. xelatex with the default Latin Modern font silently drops characters it lacks (Greek
   letters, ≤ ≥ ≈, Unicode superscripts and subscripts, arrows). Outside inline code and $...$ math,
   any character beyond ASCII, Latin-1, Latin Extended-A and common typographic punctuation is
   reported with its line. Write it as TeX math ($\\rho$, $\\le$, $10^{-12}$) or in words.
2. Brief length. The brief must print on one A4 sheet, double-sided: at most two pages.
"""

import re
import subprocess
import sys
from pathlib import Path

SAFE_EXTRA = set("–—‘’“”…×÷−°±†‡§¶·•′″€£")
STRIP = re.compile(r"`[^`\n]*`|\$[^$\n]+\$")


def safe(ch):
    o = ord(ch)
    return o < 0x80 or 0xA0 <= o <= 0x17F or ch in SAFE_EXTRA


def glyphs(path):
    problems = []
    in_fence = False
    for n, line in enumerate(Path(path).read_text().splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        bad = sorted({c for c in STRIP.sub("", line) if not safe(c)})
        if bad:
            problems.append(f"{path}:{n}: {' '.join(f'{c} (U+{ord(c):04X})' for c in bad)}")
    return problems


def pages(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True, check=True).stdout
    return int(re.search(r"^Pages:\s+(\d+)", out, re.M).group(1))


def main(argv):
    if not argv or argv[0] in {"-h", "--help"}:
        sys.exit(__doc__)
    brief, limit, sources = None, 2, []
    it = iter(argv)
    for a in it:
        if a == "--brief":
            brief = next(it)
        elif a == "--max-pages":
            limit = int(next(it))
        else:
            sources.append(a)
    problems = [p for s in sources for p in glyphs(s)]
    if brief and Path(brief).exists() and (n := pages(brief)) > limit:
        problems.append(f"{brief}: {n} pages; the brief must fit {limit}")
    for p in problems:
        print("error:", p)
    print(f"{len(sources)} sources checked; {len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
