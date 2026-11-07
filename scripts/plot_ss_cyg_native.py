#!/usr/bin/env python3
"""Plot the bounded native acquisition without normalizing time or inferring events."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.aavso import read_acquisition


def main() -> None:
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("native_xml", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("refusing to overwrite an existing figure")
    rows, summary = read_acquisition(args.native_xml)
    if not rows:
        raise ValueError("no native observations to plot")
    if set(summary["bands"]) != {"Vis."}:
        raise ValueError("this plot requires the single native visual stream")
    if not {row["val"] for row in rows} <= {"V", "T"}:
        raise ValueError("unhandled native validation flag in this plot")
    first = summary["min_native_jd"]
    fig, axes = plt.subplots(2, 1, figsize=(12, 6.5), constrained_layout=True)
    for ax, end, title in ((axes[0], summary["max_native_jd"], "Entire bounded request"),
                           (axes[1], first + 90, "First 90 native JD days")):
        for quality, flag, marker, color, label in (("V", "0", ".", "tab:blue", "Visual, V flag"),
                                                   ("V", "1", "v", "tab:orange", "Fainter-than limit, V flag"),
                                                   ("T", "0", "x", "tab:red", "Discrepant, T flag"),
                                                   ("T", "1", "v", "tab:red", "Discrepant limit, T flag")):
            subset = [row for row in rows if row["val"] == quality and row["fainterThan"] == flag
                      and first <= float(row["JD"]) <= end]
            if not subset:
                continue
            ax.scatter([float(row["JD"]) - first for row in subset], [float(row["mag"]) for row in subset],
                       marker=marker, color=color, s=12 if marker == "." else 28, alpha=0.65, label=label)
        ax.invert_yaxis()
        ax.set(xlabel=f"Native JD minus {first:.1f}", ylabel="Native visual magnitude", title=title,
               xlim=(0, end - first))
        ax.grid(alpha=0.2)
    axes[0].legend(loc="upper right", ncol=2)
    fig.suptitle("SS Cyg: bounded AAVSO native visual photometry\n"
                 "Native JD; validation flags retained; no event inference or reported uncertainties")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
