#!/usr/bin/env python3
"""Optional standard Matplotlib figure from the already-generated demo CSVs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def load_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot synthetic data only")
    parser.add_argument("run_directory", type=Path)
    args = parser.parse_args()
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit("Optional dependency missing: install Matplotlib, or inspect CSV/JSON outputs directly.") from exc
    folder = args.run_directory
    summary = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
    if summary.get("data_kind") != "SYNTHETIC ONLY":
        raise SystemExit("This plotting script is only for labelled seed simulations.")
    output = folder / "synthetic_overview.png"
    if output.exists():
        raise SystemExit(f"Refusing to overwrite {output}")
    null = load_csv(folder / "null" / "synthetic_truth.csv")
    latent = load_csv(folder / "latent" / "synthetic_truth.csv")
    phot = load_csv(folder / "null" / "synthetic_observations.csv")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    fig.suptitle("Dwarf-nova research seed • synthetic demonstrations", fontsize=17, fontweight="bold")
    ax = axes[0, 0]
    ax.scatter([float(r["duration"]) for r in null], [float(r["next_onset_gap"]) for r in null],
               s=12, alpha=0.45, color="#6574B4", label="Onset gap = duration + quiescent gap")
    ax.scatter([float(r["duration"]) for r in null], [float(r["next_quiescent_gap"]) for r in null],
               s=12, alpha=0.45, color="#D28A3D", label="Following quiescent gap")
    ax.set(title="A. Shared arithmetic can create association", xlabel="Completed duration (demo days)", ylabel="Interval (demo days)")
    ax.legend(fontsize=8, frameon=False, loc="upper right")
    ax = axes[0, 1]
    points = ax.scatter([float(r["duration"]) for r in latent], [float(r["next_quiescent_gap"]) for r in latent],
                        c=[float(r["latent_activity"]) for r in latent], cmap="viridis", s=17, alpha=0.8)
    ax.set(title="B. A shared state; no direct duration effect", xlabel="Completed duration (demo days)", ylabel="Following quiescent gap (demo days)")
    fig.colorbar(points, ax=ax, shrink=0.8, label="Injected latent activity")
    ax = axes[1, 0]
    observed = [r for r in phot if float(r["time_value"]) < 800 and r["is_upper_limit"] == "false"]
    limits = [r for r in phot if float(r["time_value"]) < 800 and r["is_upper_limit"] == "true"]
    ax.scatter([float(r["time_value"]) for r in observed], [float(r["magnitude"]) for r in observed], s=12, color="#246A73", label="Measured toy magnitude")
    ax.scatter([float(r["time_value"]) for r in limits], [float(r["limit_magnitude"]) for r in limits], s=18, marker="v", facecolors="none", edgecolors="#A46528", label="Faint limit")
    for start in (0, 365.25, 730.5):
        ax.axvspan(start, min(start + 95, 800), color="#EAECEF", zorder=0)
    ax.set(xlim=(0, 800), title="C. Seasonal gaps hide parts of the record", xlabel="Relative demo time (days)", ylabel="Synthetic V-like magnitude")
    ax.invert_yaxis()
    ax.legend(fontsize=8, frameon=False, loc="upper right")
    ax = axes[1, 1]
    names = list(summary["scenarios"])
    values = [summary["scenarios"][k]["delta_mean_log_score_M1_minus_M0"] for k in names]
    ax.bar(["Independent", "Direct effect", "Shared state", "Both"][:len(names)], values,
           color=["#AEB6BE", "#6574B4", "#246A73", "#AA7855"][:len(names)], width=0.62)
    ax.axhline(0, color="#555555", linewidth=0.8)
    ax.set(title="D. Predictive gain does not identify a mechanism", ylabel="M1 − M0 mean log predictive score")
    ax.text(0.02, 0.97, "Oracle complete events • one illustrative realization\nNo fitted latent model or uncertainty intervals", transform=ax.transAxes,
            va="top", fontsize=8.5, color="#444444")
    fig.supxlabel("All events and measurements are invented. These panels are design illustrations, not astronomical findings.", fontsize=10)
    fig.savefig(output, dpi=180, facecolor="white")
    plt.close(fig)
    print(output)


if __name__ == "__main__":
    main()
