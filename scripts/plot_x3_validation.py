#!/usr/bin/env python3
"""Plot the frozen X3 decisive cells without recomputing their intervals."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rule", choices=("C1_7", "C2_095"), required=True)
    args = parser.parse_args()
    import matplotlib.pyplot as plt

    summary = json.loads(args.summary.read_text())
    cells = [c for c in summary["cells"] if c["case"] in ("primary", "structured")
             and c["extractor"] == "X3" and c["threshold"] == "10.0"
             and c["rule"] == args.rule]
    cells.sort(key=lambda c: (c["case"], c["stratum"], c["phase"]))
    if len(cells) != 12:
        raise ValueError("exactly twelve decisive X3 cells required")
    if args.output.with_suffix(".svg").exists() or args.output.with_suffix(".png").exists():
        raise FileExistsError("refusing to overwrite figure")
    labels = [f"{c['case']}  {c['stratum'].replace('_', '–')}  {c['phase']}" for c in cells]
    fig, axes = plt.subplots(1, 4, figsize=(15, 6), sharey=True, constrained_layout=True)
    panels = (
        ("Effective coverage", (("onset_effective_coverage", "Start", "#2364aa", -.12),
                                ("end_effective_coverage", "End", "#c45715", .12))),
        ("Association bias", (("total_bias", "Extracted − oracle", "#2364aa", 0),)),
        ("Premature first signal", (("operational_confirmation_premature_fraction", "Issued events", "#2364aa", 0),)),
        ("Missing first signal", (("operational_confirmation_missing_fraction", "Unique matches", "#2364aa", 0),)),
    )
    for ax, (title, series) in zip(axes, panels):
        for field, label, color, offset in series:
            for i, cell in enumerate(cells):
                metric = cell["metrics"][field]
                value, lo, hi = (metric.get(k) for k in ("estimate", "lower", "upper"))
                if None not in (value, lo, hi):
                    ax.errorbar(value, i + offset, xerr=[[value - lo], [hi - value]],
                                fmt="o", color=color, capsize=2,
                                label=label if i == 0 else None, markersize=4)
                else:
                    ax.text(.5, i + offset, "undefined", transform=ax.get_yaxis_transform(),
                            ha="center", fontsize=8, color="#9c2323")
        ax.set_title(title, fontsize=11)
        ax.grid(axis="x", alpha=.2)
        ax.legend(fontsize=8, loc="lower right")
    axes[0].axvline(.90, color="0.4", linestyle="--", linewidth=1)
    axes[0].set_xlim(.84, 1.005)
    axes[1].axvspan(-.02, .02, color="0.90")
    axes[1].axvline(0, color="0.4", linewidth=1)
    axes[2].axvline(.02, color="0.4", linestyle="--", linewidth=1)
    axes[3].axvline(.05, color="0.4", linestyle="--", linewidth=1)
    axes[0].set_yticks(range(12), labels, fontsize=8)
    axes[0].invert_yaxis()
    verdict = next(c["verdict"] for c in summary["candidate_decisions"] if c["rule"] == args.rule)
    fig.suptitle(f"Independent X3 validation · {args.rule} · global verdict {verdict}\n"
                 "Magnitude 10 · 400 histories per cell · 95% Monte Carlo intervals",
                 fontsize=13)
    fig.supxlabel("Dashed lines and shaded band show frozen bounds; all gates, including unsafe signals, are in the decision CSV.", fontsize=9)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    svg = args.output.with_suffix(".svg")
    fig.savefig(svg)
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    fig.savefig(args.output.with_suffix(".png"), dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    main()
