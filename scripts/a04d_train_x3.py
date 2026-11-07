#!/usr/bin/env python3
"""A04d training batch for X3 (Claude): calibrate and stress-test on seeds disjoint from A04c.

Uses Codex's A04c generator, observation model and scorer unchanged, plus a
training-only morphology variant ("smooth"). The variant puts no knot at the
threshold, holds decline rate independent of duration and widens the
rise-rate spread, as the open-era light curves require (A04d memo, section 1).
It is not the validation benchmark. Needs the gitignored A04c input cache.
"""

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor
import json
import math
from pathlib import Path
import random
import statistics as st
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

BASE = "a04d-claude-training-20261107"
CONDITIONS = {
    "v1": ("v1", 1.0, 0.0),
    "smooth": ("smooth", 1.0, 0.0),
    "smooth_noise1.25": ("smooth", 1.25, 0.0),
    "smooth_noise1.5": ("smooth", 1.5, 0.0),
    "smooth_noise1.25_offsets0.2": ("smooth", 1.25, 0.2),
}
ERAS = (1, 2, 3)
INPUTS = None


def smooth_events(timing, minimum_gap, rng):
    import dnmem.injection_truth as T
    events = []
    for index, (onset, end, duration, gap, latent_d, latent_g) in enumerate(timing):
        rise = math.exp(rng.gauss(math.log(0.8), 0.7))
        decline = min(0.5, max(0.2, rng.gauss(0.33, 0.06)))
        peak = rng.uniform(9.0, 9.5) if rng.random() < 0.05 else rng.uniform(8.0, 8.8)
        amp = 10.0 - peak
        if amp * (1 / rise + 1 / decline) > 0.95 * duration:
            amp = 0.95 * duration / (1 / rise + 1 / decline)
            peak = 10.0 - amp
        knots = (T.Knot(onset - 2.2 / rise, 12.2), T.Knot(onset, 10.0), T.Knot(onset + amp / rise, peak),
                 T.Knot(end - amp / decline, peak), T.Knot(end, 10.0), T.Knot(end + 2.2 / decline, 12.2))
        events.append(T.EventTruth(index, onset, end, duration, gap, peak,
                                   "low_amplitude" if peak >= 9.0 else "standard", knots, latent_d, latent_g))
    return tuple(events)


def load(cache):
    global INPUTS
    INPUTS = json.loads(Path(cache).read_text())


def confirmation(episodes, truth, start, stop):
    from dnmem.injection_score import _matching
    confirmed = sorted((e for e in episodes if e.get("confirmed_event", True)), key=lambda e: e["peak_t"])
    ordered = sorted(truth, key=lambda e: float(e["onset"]))
    _, _, _, unique_truth = _matching(confirmed, ordered)
    lags, missing = [], 0
    for j, event in enumerate(ordered):
        if not (start + 2 <= event["onset"] and event["end"] <= stop - 2) or j not in unique_truth:
            continue
        c = confirmed[unique_truth[j]].get("confirmed")
        if c is None:
            missing += 1
        else:
            lags.append(c - event["end"])
    return lags, missing


def run_one(task):
    import dnmem.injection_truth as T
    from dnmem.injection_observe import simulate_rows
    from dnmem.injection_score import score_run
    from dnmem.extract import x1_vote_episodes, x2_median_hysteresis
    from dnmem.extract_x3 import x3_fitted_episodes
    from run_injection_recovery import seed_for

    condition, era, replicate = task
    morphology, noise, offset_sd = CONDITIONS[condition]
    original = T._build_events
    if morphology == "smooth":
        T._build_events = smooth_events
    s = INPUTS["strata"][era]
    seed = seed_for(BASE, condition, s["stratum"], replicate)
    try:
        history = T.generate_events(INPUTS["durations"], INPUTS["gaps"], s["start"], s["stop"],
                                    seed_for(seed, "truth"), process="null")
    finally:
        T._build_events = original
    rng = random.Random(seed_for(seed, "offsets"))
    model = {k: dict(v, sigma=v["sigma"] * noise, offset=v["offset"] + (rng.gauss(0, offset_sd) if offset_sd else 0.0))
             for k, v in sorted(INPUTS["model"].items())}
    rows = simulate_rows(s["schedule"], T.magnitudes_at(history, [float(r["JD"]) for r in s["schedule"]]),
                         model, seed_for(seed, "measurement"))
    truth = T.truth_catalogue(history, 10.0)
    out = []
    for name, fn in (("X1", x1_vote_episodes), ("X2", x2_median_hysteresis), ("X3", x3_fitted_episodes)):
        episodes = fn(rows)
        lags, missing = confirmation(episodes, truth, s["start"], s["stop"]) if name == "X3" else ([], 0)
        for result in score_run(rows, episodes, truth, s["start"], s["stop"], 10.0):
            if result["rule"] not in ("C1_7", "C2_095"):
                continue
            out.append({"condition": condition, "stratum": s["stratum"], "replicate": replicate, "extractor": name,
                        "confirm_n": len(lags), "confirm_missing": missing,
                        "confirm_premature": sum(x < 0 for x in lags),
                        "confirm_lag_median": st.median(lags) if lags else None, **result})
    return out


def point_errors(task):
    """Matched-event errors of X1 midpoints and X3 point estimates (smooth morphology, 1.25x noise)."""
    import dnmem.injection_truth as T
    from dnmem.injection_observe import simulate_rows
    from dnmem.injection_score import _matching
    from dnmem.extract import x1_vote_episodes
    from dnmem.extract_x3 import x3_fitted_episodes
    from run_injection_recovery import seed_for
    era, replicate = task
    original, T._build_events = T._build_events, smooth_events
    s = INPUTS["strata"][era]
    seed = seed_for("a04d-claude-midpoint-20261107", s["stratum"], replicate)
    try:
        history = T.generate_events(INPUTS["durations"], INPUTS["gaps"], s["start"], s["stop"],
                                    seed_for(seed, "truth"), process="null")
    finally:
        T._build_events = original
    model = {k: dict(v, sigma=v["sigma"] * 1.25) for k, v in INPUTS["model"].items()}
    rows = simulate_rows(s["schedule"], T.magnitudes_at(history, [float(r["JD"]) for r in s["schedule"]]),
                         model, seed_for(seed, "measurement"))
    truth = sorted(T.truth_catalogue(history, 10.0), key=lambda e: e["onset"])
    out = []
    for name, fn in (("X1", x1_vote_episodes), ("X3", x3_fitted_episodes)):
        episodes = sorted((e for e in fn(rows) if e["confirmed_event"]), key=lambda e: e["peak_t"])
        for j, i in _matching(episodes, truth)[3].items():
            e = episodes[i]
            if None in (e["onset_lo"], e["onset_hi"], e["end_lo"], e["end_hi"]):
                continue
            on = e.get("onset_t", (e["onset_lo"] + e["onset_hi"]) / 2)
            end = e.get("end_t", (e["end_lo"] + e["end_hi"]) / 2)
            out.append((name, on - truth[j]["onset"], end - truth[j]["end"]))
    return out


def summarise_points(errors):
    table = []
    for name in ("X1", "X3"):
        for side, k in (("onset", 1), ("end", 2)):
            xs = sorted(e[k] for e in errors if e[0] == name)
            table.append({"extractor": name, "boundary": side, "matched": len(xs),
                          "median_abs_error_d": round(st.median(abs(x) for x in xs), 3),
                          "rmse_d": round(math.sqrt(st.mean(x * x for x in xs)), 3),
                          "q05_d": round(xs[int(0.05 * (len(xs) - 1))], 3), "q95_d": round(xs[int(0.95 * (len(xs) - 1))], 3)})
    return table


def summarise(rows):
    keys = ("onset_effective_coverage", "end_effective_coverage", "onset_conditional_coverage",
            "end_conditional_coverage", "onset_mean_width", "end_mean_width", "unique_completeness",
            "false_confirmed_per_year", "total_bias")
    cells = {}
    for r in rows:
        cells.setdefault((r["condition"], r["stratum"], r["extractor"], r["rule"]), []).append(r)
    table = []
    for (condition, stratum, extractor, rule), rs in sorted(cells.items()):
        row = {"condition": condition, "stratum": stratum, "extractor": extractor, "rule": rule, "replicates": len(rs)}
        for k in keys:
            xs = [r[k] for r in rs if r.get(k) is not None]
            row[k] = round(st.mean(xs), 4) if xs else ""
            row[k + "_se"] = round(st.stdev(xs) / math.sqrt(len(xs)), 4) if len(xs) > 1 else ""
        n = sum(r["confirm_n"] for r in rs)
        row["confirm_premature_rate"] = round(sum(r["confirm_premature"] for r in rs) / n, 4) if n else ""
        row["confirm_missing_rate"] = round(sum(r["confirm_missing"] for r in rs) / (n + sum(r["confirm_missing"] for r in rs)), 4) if n else ""
        lags = [r["confirm_lag_median"] for r in rs if r["confirm_lag_median"] is not None]
        row["confirm_lag_median"] = round(st.median(lags), 3) if lags else ""
        table.append(row)
    return table


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=ROOT / "outputs/a04c_inputs_final_20261107/inputs.json")
    parser.add_argument("--replicates", type=int, default=40)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--raw", type=Path, default=ROOT / "outputs/a04d_x3_training_20261107.json")
    parser.add_argument("--table", type=Path, default=ROOT / "data/simulations/a04d_x3_training_20261107.csv")
    parser.add_argument("--points", type=Path, help="instead, write the point-estimate check here (12 replicates per era)")
    args = parser.parse_args()
    if args.points:
        with ProcessPoolExecutor(args.workers, initializer=load, initargs=(args.inputs,)) as pool:
            errors = [e for chunk in pool.map(point_errors, [(e, r) for e in ERAS for r in range(12)]) for e in chunk]
        table = summarise_points(errors)
        with open(args.points, "w", newline="") as h:
            writer = csv.DictWriter(h, fieldnames=list(table[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(table)
        print(table)
        return
    tasks = [(c, e, r) for c in CONDITIONS for e in ERAS for r in range(args.replicates)]
    with ProcessPoolExecutor(args.workers, initializer=load, initargs=(args.inputs,)) as pool:
        rows = [r for chunk in pool.map(run_one, tasks, chunksize=2) for r in chunk]
    args.raw.write_text(json.dumps(rows, default=str))
    table = summarise(rows)
    with open(args.table, "w", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=list(table[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(table)
    for row in table:
        if row["rule"] == "C1_7":
            print(row["condition"], row["stratum"], row["extractor"], "eff on/end", row["onset_effective_coverage"],
                  row["end_effective_coverage"], "cond", row["onset_conditional_coverage"], row["end_conditional_coverage"],
                  "w", row["onset_mean_width"], row["end_mean_width"], "bias", row["total_bias"], row["total_bias_se"],
                  "prem", row["confirm_premature_rate"], "lag", row["confirm_lag_median"])


if __name__ == "__main__":
    main()
