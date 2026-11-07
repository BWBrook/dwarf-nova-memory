#!/usr/bin/env python3
"""Apply A04 protocol v1 mechanically: local candidates, boundary listings, review figures."""

import argparse
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.aavso import read_acquisition
from dnmem.brackets import THRESHOLD, bounds, candidate_runs, coverage_gaps, row_class

WINDOW = 70.0
CONTEXT = 3.0


def jd(row):
    return float(row["JD"]) if row is not None else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("native_xml", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("refusing to reuse an existing output directory")
    rows, summary = read_acquisition(args.native_xml)
    runs = candidate_runs(rows)
    gaps = coverage_gaps(rows)
    args.output.mkdir(parents=True)

    fields = ["candidate", "onset_earliest_jd", "onset_latest_jd", "end_earliest_jd", "end_latest_jd",
              "onset_detected_jd", "end_confirmed_jd", "duration_min", "duration_max", "gap_min",
              "gap_max", "n_bright", "n_bright_observers", "peak_mag", "peak_jd"]
    with open(args.output / "candidates.csv", "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for k, run in enumerate(runs):
            b = bounds(run, runs[k + 1] if k + 1 < len(runs) else None)
            writer.writerow({"candidate": k + 1, "onset_earliest_jd": jd(run["onset_earliest"]),
                             "onset_latest_jd": jd(run["onset_latest"]),
                             "end_earliest_jd": jd(run["end_earliest"]), "end_latest_jd": jd(run["end_latest"]),
                             "onset_detected_jd": jd(run["onset_detected"]),
                             "end_confirmed_jd": jd(run["end_confirmed"]),
                             "duration_min": b["duration_min"], "duration_max": b["duration_max"],
                             "gap_min": b["gap_min"], "gap_max": b["gap_max"], "n_bright": run["n_bright"],
                             "n_bright_observers": run["n_bright_observers"],
                             "peak_mag": run["peak"]["mag"], "peak_jd": jd(run["peak"])})

    ordered = sorted(rows, key=lambda row: (float(row["JD"]), row["obsID"]))
    observers = {}
    with open(args.output / "boundary_rows.txt", "w") as handle:
        for k, run in enumerate(runs):
            handle.write(f"\n=== candidate {k + 1}\n")
            for label, centre in (("onset", jd(run["onset_latest"])), ("end", jd(run["end_earliest"]))):
                handle.write(f"--- {label} near {centre}\n")
                for row in ordered:
                    if abs(float(row["JD"]) - centre) <= CONTEXT:
                        who = observers.setdefault(row.get("obsName") or row["by"], f"o{len(observers) + 1:02d}")
                        handle.write(f"{row['JD']:>12} {'<' if row['fainterThan'] == '1' else ' '}"
                                     f"{row['mag']:>5} {row_class(row)} val={row['val']} "
                                     f"com={row.get('comCode') or '-':3} {who} id={row['obsID']}\n")
        handle.write("\n=== coverage gaps > 4 d between informative V rows\n")
        for a, b in gaps:
            handle.write(f"{a} -> {b} ({b - a:.1f} d)\n")

    import matplotlib.pyplot as plt
    start, end = summary["min_native_jd"], summary["max_native_jd"]
    windows = []
    t = start
    while t < end:
        windows.append((t, min(t + WINDOW, end + 0.5)))
        t += WINDOW - 5.0
    per_page = 4
    for page in range(0, len(windows), per_page):
        chunk = windows[page:page + per_page]
        fig, axes = plt.subplots(len(chunk), 1, figsize=(13, 3.1 * len(chunk)), constrained_layout=True)
        axes = [axes] if len(chunk) == 1 else list(axes)
        for ax, (a, b) in zip(axes, chunk):
            for cls, val, limit, marker, color, label in (
                    ("B", "V", "0", "o", "tab:blue", "B estimate"), ("F", "V", "0", "o", "tab:gray", "F estimate"),
                    ("F", "V", "1", "v", "tab:gray", "F limit"), ("N", "V", "1", "v", "tab:orange", "N limit"),
                    (None, "T", None, "x", "tab:red", "T flag")):
                sub = [row for row in rows if a <= float(row["JD"]) <= b and row["val"] == val
                       and (cls is None or row_class(row) == cls) and (limit is None or row["fainterThan"] == limit)]
                if sub:
                    ax.scatter([float(r["JD"]) - start for r in sub], [float(r["mag"]) for r in sub],
                               marker=marker, color=color, s=14, alpha=0.7, label=label)
            for k, run in enumerate(runs):
                lo, hi = jd(run["onset_earliest"]) or jd(run["onset_latest"]), jd(run["end_latest"]) or jd(run["end_earliest"])
                if hi >= a and lo <= b:
                    ax.axvspan(lo - start, jd(run["onset_latest"]) - start, color="tab:green", alpha=0.25)
                    ax.axvspan(jd(run["end_earliest"]) - start, hi - start, color="tab:purple", alpha=0.25)
                    ax.text(jd(run["onset_latest"]) - start, 7.6, str(k + 1), fontsize=8)
            for g0, g1 in gaps:
                if g1 >= a and g0 <= b:
                    ax.axvspan(g0 - start, g1 - start, color="yellow", alpha=0.3)
            ax.axhline(THRESHOLD, color="k", lw=0.6, ls="--")
            ax.set(xlim=(a - start, b - start), ylim=(13.5, 7.3), ylabel="native vis. mag")
            ax.grid(alpha=0.2)
        axes[0].legend(loc="lower right", ncol=5, fontsize=7)
        axes[-1].set_xlabel(f"native JD − {start}")
        fig.suptitle("SS Cyg 1956–1958, AAVSO visual (real data). Green: onset bracket; purple: end bracket; "
                     "yellow: >4 d gap; dashed: m*=10. Mechanical A04-v1 candidates, not adjudicated.", fontsize=9)
        fig.savefig(args.output / f"review_{page // per_page + 1:02d}.png", dpi=110)
        plt.close(fig)
    print(f"{len(runs)} candidates, {len(gaps)} gaps > 4 d; outputs in {args.output}")


if __name__ == "__main__":
    main()
