#!/usr/bin/env python3
"""Plot synthetic recovery coverage and null-bias screening metrics."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    import matplotlib.pyplot as plt

    cells = json.loads(args.summary.read_text())["cells"]
    cells = [r for r in cells if r["phase"] == "random" and r["process"] == "null" and float(r["threshold"]) == 10]
    strata = ("1900_1909", "1910_1929", "1930_1949", "1950_1959")
    colors = {"X1": "#2364aa", "X2": "#c45715"}
    fig, (left, right) = plt.subplots(1, 2, figsize=(12, 4.7), constrained_layout=True)
    for candidate in ("X1", "X2"):
        for boundary, style in (("onset", "-"), ("end", "--")):
            selected = [next(r for r in cells if r["stratum"] == s and r["extractor"] == candidate and r["rule"] == "C1_7") for s in strata]
            metrics = [r["metrics"][boundary + "_coverage"] for r in selected]
            values = [m["estimate"] for m in metrics]
            left.errorbar(range(4), values, yerr=[1.96*m["mcse"] for m in metrics], color=colors[candidate],
                          linestyle=style, marker="o", capsize=3, label=candidate+" "+boundary)
        for index, (rule, marker) in enumerate((("C1_4", "o"), ("C1_7", "^"), ("C2_095", "s"))):
            selected = [next(r for r in cells if r["stratum"] == s and r["extractor"] == candidate and r["rule"] == rule) for s in strata]
            offset = -.22 + index*.08 + (0 if candidate == "X1" else .25)
            labelled = False
            for x, row in enumerate(selected):
                metric = row["metrics"]["total_bias"]
                if metric["estimate"] is not None and metric["mcse"] is not None and metric["undefined"] == 0:
                    right.errorbar(x+offset, metric["estimate"], yerr=1.96*metric["mcse"], color=colors[candidate],
                                   marker=marker, linestyle="none", capsize=2,
                                   label=candidate+" "+rule if not labelled else None)
                    labelled = True
    left.axhline(.9, color="0.4", linewidth=1)
    left.set(ylabel="Effective interval coverage", ylim=(0, 1.02), title="Truth inside reported boundaries")
    right.axhspan(-.02, .02, color="0.9")
    right.axhline(0, color="0.4", linewidth=1)
    right.set(ylabel="Recovered − oracle partial correlation", title="Total bias (undefined cells omitted)")
    for ax in (left, right):
        ax.set_xticks(range(4), ("1900–09", "1910–29", "1930–49", "1950–59"))
        ax.grid(axis="y", alpha=.2)
        ax.legend(fontsize=8, ncols=2)
    fig.suptitle("Synthetic outburst recovery at the fixed pre-1960 SS Cyg cadence\n"
                 "Random renewal null · magnitude 10 · 95% Monte Carlo intervals")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    svg = args.output.with_suffix(".svg")
    fig.savefig(svg)
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    fig.savefig(args.output.with_suffix(".png"), dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    main()
