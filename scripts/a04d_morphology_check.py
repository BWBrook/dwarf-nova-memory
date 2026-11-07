#!/usr/bin/env python3
"""Posterior predictive check of injection benchmarks against open-era SS Cyg light curves.

Applies one estimator to real 1910-1959 rows and to synthetic rows: around each
X1 episode boundary, a Theil-Sen line through observer-visit estimates within
1 mag of 10.0. Reports local slope, residual scatter, estimates per window,
decline slope against episode duration, and decline slopes in the 1 mag
above and below the threshold. No duration-gap association is computed.
Needs the gitignored native exports and A04c input cache.
"""

import argparse
import json
import math
from pathlib import Path
import statistics as st
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from dnmem.extract import visits, x1_vote_episodes

J1910, J1960, THR = 2418672.5, 2436934.5, 10.0
SEED = "a04d-claude-morphology-20261107"


def theil_sen(points):
    if len(points) < 4 or max(x for x, _ in points) - min(x for x, _ in points) < 0.4:
        return None
    slopes = [(y2 - y1) / (x2 - x1) for i, (x1, y1) in enumerate(points) for x2, y2 in points[i + 1:] if x2 - x1 > 0.05]
    if len(slopes) < 3:
        return None
    s = st.median(slopes)
    a = st.median(y - s * x for x, y in points)
    return s, 1.4826 * st.median(abs(y - a - s * x) for x, y in points)


def windows(rows):
    votes = [v for v in visits(rows, THR) if v["value"] is not None]
    out = []
    for e in x1_vote_episodes(rows):
        if not e["confirmed_event"] or e["gap_split"] or None in (e["onset_lo"], e["onset_hi"], e["end_lo"], e["end_hi"]):
            continue
        if not J1910 <= e["peak_t"] < J1960:
            continue
        on = [(v["t"] - e["onset_lo"], v["value"]) for v in votes if e["onset_lo"] - 1 <= v["t"] <= e["onset_hi"] + 1
              and v["t"] < e["peak_t"] and abs(v["value"] - THR) <= 1.0]
        end = [(v["t"] - e["end_lo"], v["value"]) for v in votes if e["end_lo"] - 2 <= v["t"] <= e["end_hi"] + 2
               and v["t"] > e["peak_t"] and abs(v["value"] - THR) <= 1.0]
        wide = [(v["t"] - e["end_lo"], v["value"]) for v in votes if e["end_lo"] - 3 <= v["t"] <= e["end_hi"] + 3 and v["t"] > e["peak_t"]]
        out.append({"duration": (e["end_lo"] + e["end_hi"] - e["onset_lo"] - e["onset_hi"]) / 2,
                    "onset": theil_sen(on), "end": theil_sen(end), "n_onset": len(on), "n_end": len(end),
                    "above": theil_sen([p for p in wide if THR - 1 <= p[1] <= THR]),
                    "below": theil_sen([p for p in wide if THR < p[1] <= THR + 1])})
    return out


def quantiles(xs):
    xs = sorted(xs)
    return {f"q{int(100 * p)}": round(xs[int(p * (len(xs) - 1))], 3) for p in (.1, .25, .5, .75, .9)} | {"n": len(xs)} if xs else {}


def spearman(xs, ys):
    rank = lambda v: {x: i for i, x in enumerate(sorted(v))}
    rx, ry = rank(xs), rank(ys)
    a, b = [rx[x] for x in xs], [ry[y] for y in ys]
    ma, mb = st.mean(a), st.mean(b)
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))


def summary(recs):
    out = {"episodes": len(recs)}
    for side, sign in (("onset", -1), ("end", 1)):
        fits = [r[side] for r in recs if r[side] and r[side][0] * sign > 0]
        out[side] = {"abs_slope_mag_per_d": quantiles([abs(f[0]) for f in fits]),
                     "residual_sd_mag": quantiles([f[1] for f in fits]),
                     "estimates_in_window": quantiles([r["n_" + side] for r in recs])}
    pairs = [(r["duration"], r["end"][0]) for r in recs if r["end"] and r["end"][0] > 0]
    out["end_slope_vs_duration_spearman"] = round(spearman(*zip(*pairs)), 3)
    out["end_slope_median_short_lt11d"] = round(st.median(s for d, s in pairs if d < 11), 3)
    out["end_slope_median_long_ge11d"] = round(st.median(s for d, s in pairs if d >= 11), 3)
    for part in ("above", "below"):
        fits = [r[part][0] for r in recs if r[part] and r[part][0] > 0]
        out[f"decline_slope_{part}_threshold"] = quantiles(fits)
    return out


def synthetic(morphology, inputs, replicates, noise=1.0):
    import dnmem.injection_truth as T
    from dnmem.injection_observe import simulate_rows
    from run_injection_recovery import seed_for
    from a04d_train_x3 import smooth_events
    recs = []
    original = T._build_events
    if morphology == "smooth":
        T._build_events = smooth_events
    try:
        for s in inputs["strata"][1:]:
            for rep in range(replicates):
                seed = seed_for(SEED, morphology, s["stratum"], rep)
                h = T.generate_events(inputs["durations"], inputs["gaps"], s["start"], s["stop"], seed_for(seed, "truth"), process="null")
                model = {k: dict(v, sigma=v["sigma"] * noise) for k, v in inputs["model"].items()}
                rows = simulate_rows(s["schedule"], T.magnitudes_at(h, [float(r["JD"]) for r in s["schedule"]]),
                                     model, seed_for(seed, "measurement"))
                recs += windows(rows)
    finally:
        T._build_events = original
    return recs


def main():
    from dnmem.coverage import combine_acquisitions
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=ROOT / "outputs/a04c_inputs_final_20261107/inputs.json")
    parser.add_argument("--replicates", type=int, default=6)
    parser.add_argument("--output", type=Path, default=ROOT / "data/simulations/a04d_morphology_check_20261107.json")
    args = parser.parse_args()
    rows, _ = combine_acquisitions(sorted((ROOT / "data/raw").glob("aavso_ss_cyg_*/native.xml")))
    rows = [r for r in rows if float(r["JD"]) < J1960]
    inputs = json.loads(args.inputs.read_text())
    result = {"estimator": __doc__.strip().splitlines()[0], "synthetic_seed_base": SEED,
              "synthetic_replicates_per_era": args.replicates,
              "real_1910_1959": summary(windows(rows)),
              "a04c_v1_benchmark": summary(synthetic("v1", inputs, args.replicates)),
              "claude_training_smooth": summary(synthetic("smooth", inputs, args.replicates)),
              "claude_training_smooth_noise1.25": summary(synthetic("smooth", inputs, args.replicates, 1.25))}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
