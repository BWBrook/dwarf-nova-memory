#!/usr/bin/env python3
"""A10c: re-aggregate the A10b control scores by route and under the proposed A10c design.

Reads the retained A10b repaired-run outputs (scores.jsonl and per-trial records; not in Git).
Writes a compact JSON summary. For each family/case/variant it reports, per trial:

- the reported M3-M2 mean gain (all scored issuances);
- the part from issuances where M3 used its full architecture (route M3) and the part where
  a missing covered previous gap sent M3 to M1 and M2 to M0 (route M1);
- the fitted M3 duration coefficient;
- the A10c design gain: route-M1 issuances contribute zero (matched routing), and a trial
  whose fitted coefficient is negative contributes zero (directional M3, beta >= 0). Under a
  unimodal likelihood the constrained optimum is beta = 0 whenever the unconstrained optimum
  is negative, so M3 then reproduces M2 up to rows lacking duration.

No real observation, outcome or duration-gap association is read.
"""

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import statistics as st

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ("prefix_point", "prefix_uniform_end", "retrospective_point", "oracle_point")
T975 = {3: 3.182, 7: 2.365}


def interval(values):
    m = st.fmean(values)
    se = st.stdev(values) / math.sqrt(len(values))
    t = T975[len(values) - 1]
    return {"mean": round(m, 5), "trial_sd": round(st.stdev(values), 5),
            "mc95": [round(m - t * se, 5), round(m + t * se, 5)], "positive": sum(v > 0 for v in values),
            "trials": len(values)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT / "outputs/a10b_controls_repaired_20261108")
    parser.add_argument("--output", type=Path, default=ROOT / "data/simulations/a10c_reaggregated_controls_20261108.json")
    args = parser.parse_args()
    sums = defaultdict(lambda: {"all": 0.0, "M3": 0.0, "M1": 0.0, "n": 0, "n_M1": 0})
    with (args.input_dir / "scores.jsonl").open() as handle:
        for line in handle:
            r = json.loads(line)
            if r["variant"] not in VARIANTS or r["gain_M3_M2"] is None:
                continue
            s = sums[(r["family"], r["case"], r["variant"], r["replicate"])]
            s["n"] += 1
            s["all"] += r["gain_M3_M2"]
            if r["route_M3"] == "M3":
                s["M3"] += r["gain_M3_M2"]
            elif r["route_M3"] == "M1":
                s["M1"] += r["gain_M3_M2"]
                s["n_M1"] += 1
    betas = {}
    for key in {k[:2] + (k[3],) for k in sums}:
        family, case, replicate = key
        record = json.loads((args.input_dir / f"{family}-{case}-{replicate:03d}.json").read_text())["result"]
        for variant in VARIANTS:
            if variant in record["models"]:
                betas[(family, case, variant, replicate)] = record["models"][variant]["models"]["M3"]["coefficients"]["duration"]
    groups = defaultdict(list)
    for key, s in sums.items():
        family, case, variant, replicate = key
        beta = betas[key]
        groups[(family, case, variant)].append({
            "replicate": replicate, "issuances": s["n"], "route_M1_share": s["n_M1"] / s["n"],
            "beta_duration": beta, "reported": s["all"] / s["n"], "route_M3_part": s["M3"] / s["n"],
            "route_M1_part": s["M1"] / s["n"], "a10c_design": (s["M3"] / s["n"]) if beta > 0 else 0.0})
    out = {"source": str(args.input_dir.relative_to(ROOT)) if args.input_dir.is_relative_to(ROOT) else str(args.input_dir),
           "note": __doc__.strip().splitlines()[0], "groups": []}
    for (family, case, variant), trials in sorted(groups.items()):
        trials.sort(key=lambda t: t["replicate"])
        row = {"family": family, "case": case, "variant": variant,
               "route_M1_share": round(st.fmean(t["route_M1_share"] for t in trials), 4),
               "beta_duration": interval([t["beta_duration"] for t in trials]),
               "negative_beta_trials": sum(t["beta_duration"] < 0 for t in trials)}
        for name in ("reported", "route_M3_part", "route_M1_part", "a10c_design"):
            row[name] = interval([t[name] for t in trials])
        row["trials"] = [{k: (round(v, 6) if isinstance(v, float) else v) for k, v in t.items()} for t in trials]
        out["groups"].append(row)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    for row in out["groups"]:
        if row["variant"] in ("prefix_point", "prefix_uniform_end"):
            print(f"{row['family']:9s} {row['case']:11s} {row['variant']:19s} M1share {row['route_M1_share']:.3f} "
                  f"reported {row['reported']['mean']:+.5f} routeM3 {row['route_M3_part']['mean']:+.5f} "
                  f"routeM1 {row['route_M1_part']['mean']:+.5f} | A10c {row['a10c_design']['mean']:+.5f} "
                  f"sd {row['a10c_design']['trial_sd']:.5f} {row['a10c_design']['mc95']} beta<0 {row['negative_beta_trials']}")


if __name__ == "__main__":
    main()
