#!/usr/bin/env python3
"""Plot the recorded A04g qualification, without recomputing a gate."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    import matplotlib.pyplot as plt

    record = json.loads(args.record.read_text())
    series = [("Real", record["real_morphology"]["10.0"], "#222222")]
    for family, color in (("v2", "#2364aa"), ("v3", "#c45715")):
        for phase in ("random", "diverse"):
            series.append((f"{family} {phase}", record["families"][family][phase]["summaries"]["10.0"], color))
    if args.output.with_suffix(".svg").exists() or args.output.with_suffix(".png").exists():
        raise FileExistsError("refusing to overwrite figure")
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.3), sharey=True, constrained_layout=True)
    real_rho = series[0][1]["end_slope_vs_duration_spearman"]
    right.axvspan(real_rho - .15, real_rho + .15, color="0.92")
    right.axvline(real_rho - .15, color="0.45", linestyle="--", linewidth=1)
    right.axvline(real_rho, color="0.45", linewidth=1)
    for y, (label, summary, color) in enumerate(series):
        q = summary["end"]["abs_slope_mag_per_d"]
        left.plot([q["q10"], q["q90"]], [y, y], color=color, linewidth=1.5)
        left.plot([q["q25"], q["q75"]], [y, y], color=color, linewidth=7, solid_capstyle="butt")
        left.plot(q["q50"], y, "o", color=color, markersize=6, markeredgecolor="white")
        rho = summary["end_slope_vs_duration_spearman"]
        right.plot(rho, y, "o", color=color)
        right.annotate(f"{rho:+.3f}" + ("  FAIL" if label == "v3 diverse" and not record["all_passed"] else ""),
                       (rho, y), xytext=(8, -4), textcoords="offset points", fontsize=9)
    left.set_yticks(range(5), [x[0] for x in series])
    left.invert_yaxis()
    left.set(title="Measured decline speeds", xlabel="mag/day · median, quartiles and 10–90% quantiles")
    right.set(title="Decline-speed–duration correlation", xlabel="Spearman rho · shading is the frozen allowed range", xlim=(-.14, .20))
    for ax in (left, right):
        ax.grid(axis="x", alpha=.2)
    fig.suptitle("A04g: benchmark qualification failed; X4 recovery not run\n"
                 "32 fresh histories per era / family / cadence · freeze b83d76a", fontsize=12)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    svg = args.output.with_suffix(".svg")
    fig.savefig(svg)
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    fig.savefig(args.output.with_suffix(".png"), dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
