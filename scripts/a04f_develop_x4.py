#!/usr/bin/env python3
"""A04f development evidence (Claude): X3 versus X4, and observer diversity, on seeds disjoint from A04e.

Default mode scores X3 (with the A04e causal wrapper) and X4 (with its own
causal rule) on two families, both cadence arms and the three decisive eras:
the A04e v2 benchmark (Codex's generator, observation model and state cadence,
diagnosis seeds) and Claude's training "smooth" family. X4's SYSTEMATIC
constant was chosen on the smooth family. `--diversity` compares distinct
bright observers per outburst-sized X1 episode in real 1910-1959 rows with both
v2 cadence arms, and counts real episodes that only X4's single-observer rule
confirms. No duration-gap association is computed. Needs the gitignored A04e
input cache and native exports.
"""

import argparse
import bisect
import csv
from concurrent.futures import ProcessPoolExecutor
import json
import math
from pathlib import Path
import statistics as st
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

BASE = "a04f-claude-development-20261108"
CACHE = ROOT / "outputs/a04e_inputs_verified_20261107/inputs.json"
PARAMS = ROOT / "configs/a04e_benchmark.json"
STATE = {}


def init():
    STATE["inputs"] = json.loads(CACHE.read_text())
    STATE["params"] = json.loads(PARAMS.read_text())


def history(family, era, phase, replicate, base=BASE):
    from run_x3_validation import _copy_model, seed_for, select_strata
    from dnmem.injection_observe import simulate_rows
    from dnmem.x3_observation import state_compatible_schedule
    inputs, params = STATE["inputs"], STATE["params"]
    s = select_strata(inputs)[0][era]
    start, stop = float(s["start"]), float(s["stop"])
    seed = seed_for(base, family, s["stratum"], phase, replicate)
    if family == "v2":
        from dnmem.injection_truth_v2 import ShapeConfig, generate_events, magnitudes_at, truth_catalogue
        h = generate_events(inputs["durations"], inputs["gaps"], start, stop, seed_for(seed, "truth"),
                            process="null", shape_config=ShapeConfig(**params["shape_config"]))
        model = _copy_model(inputs["brightness_model"], float(params["noise_multiplier"]))
    else:
        import dnmem.injection_truth as T
        from a04d_train_x3 import smooth_events
        original, T._build_events = T._build_events, smooth_events
        try:
            h = T.generate_events(inputs["durations"], inputs["gaps"], start, stop, seed_for(seed, "truth"), process="null")
        finally:
            T._build_events = original
        magnitudes_at, truth_catalogue = T.magnitudes_at, T.truth_catalogue
        model = _copy_model(inputs["brightness_model"], 1.0)
    schedule = list(s["schedule"])
    if phase == "state":
        schedule, _ = state_compatible_schedule(s["days"], h, start, stop)
    rows = simulate_rows(schedule, magnitudes_at(h, [float(r.get("t", r["JD"])) for r in schedule]),
                         model, seed_for(seed, "measurement"))
    return rows, sorted(truth_catalogue(h, 10.0), key=lambda e: float(e["onset"])), start, stop


def score(rows, episodes, emissions, truth, start, stop):
    from dnmem.injection_score import _matching
    from dnmem.x3_validation_score import _operational_confirmation_metrics
    confirmed = sorted((e for e in episodes if e["confirmed_event"]), key=lambda e: e["peak_t"])
    unconfirmed = [e for e in episodes if not e["confirmed_event"]]
    ep_edges, truth_edges, _, unique = _matching(confirmed, truth)
    ref = [j for j, t in enumerate(truth) if start + 2 <= float(t["onset"]) and float(t["end"]) <= stop - 2]
    out = {"reference": len(ref), "false": sum(not n for n in ep_edges.values()), "years": (stop - start) / 365.25,
           "missed": 0, "unconfirmed": 0, "split": 0, "nonunique": 0}
    for j in ref:
        if j in unique:
            continue
        on, end = float(truth[j]["onset"]), float(truth[j]["end"])
        if not truth_edges[j]:
            hit = any(on - 0.5 <= e["peak_t"] <= end + 0.5 for e in unconfirmed)
            out["unconfirmed" if hit else "missed"] += 1
        else:
            out["split" if len(truth_edges[j]) > 1 else "nonunique"] += 1
    for b in ("onset", "end"):
        covered = finite = 0
        width = 0.0
        for j in ref:
            if j not in unique:
                continue
            e = confirmed[unique[j]]
            lo, hi = e[b + "_lo"], e[b + "_hi"]
            if lo is None or hi is None or hi <= lo:
                continue
            finite += 1
            covered += lo <= float(truth[j][b]) <= hi
            width += hi - lo
        out[b + "_covered"], out[b + "_finite"], out[b + "_width"] = covered, finite, width
    op = _operational_confirmation_metrics(ref, [j for j in ref if j in unique], truth, emissions)
    lags = [r["lag"] for r in op["operational_confirmation_first_records"] if r["lag"] is not None]
    out.update({"causal_false": op["operational_confirmation_false_emission_count"],
                "causal_ambiguous": op["operational_confirmation_ambiguous_emission_count"],
                "causal_missing": op["operational_confirmation_missing_count"],
                "causal_candidates": op["operational_confirmation_candidate_count"],
                "causal_premature": op["operational_confirmation_premature_count"],
                "causal_issued": op["operational_confirmation_observed_count"], "lags": lags})
    return out


def run_one(task):
    from dnmem.extract_x3 import x3_fitted_episodes
    from dnmem.extract_x4 import causal_confirmations, x4_episodes
    from dnmem.x3_validation_score import causal_confirmation_emissions
    rows, truth, start, stop = history(*task)
    return task, {"X3": score(rows, x3_fitted_episodes(rows), causal_confirmation_emissions(rows), truth, start, stop),
                  "X4": score(rows, x4_episodes(rows), causal_confirmations(rows), truth, start, stop)}


def summarise(results):
    table = []
    cells = {}
    for (family, era, phase, _), out in results:
        for name, r in out.items():
            cells.setdefault((family, era, phase, name), []).append(r)
    labels = {1: "1910_1929", 2: "1930_1949", 3: "1950_1959"}
    for (family, era, phase, name), rs in sorted(cells.items()):
        a = lambda k: sum(r[k] for r in rs)
        ref, years = a("reference"), a("years")
        lags = [x for r in rs for x in r["lags"]]
        row = {"family": family, "stratum": labels[era], "phase": phase, "extractor": name, "histories": len(rs),
               "reference_events": ref}
        for b in ("onset", "end"):
            row[b + "_effective_coverage"] = round(a(b + "_covered") / ref, 4)
            per = [r[b + "_covered"] / r["reference"] for r in rs]
            row[b + "_effective_se"] = round(st.stdev(per) / math.sqrt(len(per)), 4)
            row[b + "_conditional_coverage"] = round(a(b + "_covered") / a(b + "_finite"), 4)
            row[b + "_mean_width_d"] = round(a(b + "_width") / a(b + "_finite"), 3)
        for k in ("missed", "unconfirmed", "split", "nonunique"):
            row[k + "_rate"] = round(a(k) / ref, 4)
        row["false_confirmed_per_year"] = round(a("false") / years, 4)
        row["causal_unsafe_per_year"] = round((a("causal_false") + a("causal_ambiguous")) / years, 4)
        row["causal_false_per_year"] = round(a("causal_false") / years, 4)
        row["causal_missing_rate"] = round(a("causal_missing") / a("causal_candidates"), 4)
        row["causal_premature_rate"] = round(a("causal_premature") / a("causal_issued"), 4)
        row["causal_lag_median_d"] = round(st.median(lags), 3)
        table.append(row)
    return table


def diversity(replicates):
    from run_x3_validation import select_strata
    from dnmem.coverage import combine_acquisitions
    from dnmem.extract import x1_vote_episodes
    from dnmem.extract_x3 import x3_fitted_episodes
    from dnmem.extract_x4 import x4_episodes

    def bright_observers(rows, lo, hi):
        return [e["n_bright_observers"] for e in x1_vote_episodes(rows) if lo <= e["peak_t"] < hi
                and e["onset_lo"] is not None and e["end_hi"] is not None and e["end_hi"] - e["onset_lo"] >= 4]

    def describe(xs):
        xs = sorted(xs)
        return {"episodes": len(xs), "median": st.median(xs), "q10": xs[int(0.1 * (len(xs) - 1))],
                "q25": xs[int(0.25 * (len(xs) - 1))], "share_le_1": round(sum(x <= 1 for x in xs) / len(xs), 4),
                "share_le_2": round(sum(x <= 2 for x in xs) / len(xs), 4)}

    init()
    real, _ = combine_acquisitions(sorted((ROOT / "data/raw").glob("aavso_ss_cyg_*/native.xml")))
    real = [r for r in real if 2418672.5 <= float(r["JD"]) < 2436934.5]
    strata = select_strata(STATE["inputs"])[0]
    result = {"measure": "distinct bright observers per X1 episode spanning at least 4 d",
              "seed_base": BASE + "-diversity", "replicates_per_era_phase": replicates}
    with ProcessPoolExecutor(6, initializer=init) as pool:
        synthetic = list(pool.map(_diversity_one, [(e, p, r) for e in (1, 2, 3) for p in ("random", "state")
                                                  for r in range(replicates)]))
    for era, label in ((1, "1910_1929"), (2, "1930_1949"), (3, "1950_1959")):
        lo, hi = float(strata[era]["start"]), float(strata[era]["stop"])
        result[label] = {"real": describe(bright_observers(real, lo, hi))}
        for phase in ("random", "state"):
            result[label]["v2_" + phase] = describe([x for e, p, xs in synthetic if e == era and p == phase for x in xs])
    x3 = x3_fitted_episodes(real)
    x4 = x4_episodes(real)
    result["real_1910_1959_x4"] = {"confirmed_by_two_observers": sum(e["confirmation"] == "observers" for e in x4),
                                   "confirmed_by_single_observer_rule": sum(e["confirmation"] == "single_observer" for e in x4),
                                   "unconfirmed": sum(not e["confirmed_event"] for e in x4),
                                   "x3_confirmed": sum(e["confirmed_event"] for e in x3)}
    return result


def _diversity_one(task):
    from dnmem.extract import x1_vote_episodes
    era, phase, replicate = task
    rows, _, start, stop = history("v2", era, phase, replicate, BASE + "-diversity")
    return era, phase, [e["n_bright_observers"] for e in x1_vote_episodes(rows) if start <= e["peak_t"] < stop
                        and e["onset_lo"] is not None and e["end_hi"] is not None and e["end_hi"] - e["onset_lo"] >= 4]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=40)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--table", type=Path, default=ROOT / "data/simulations/a04f_x4_development_20261108.csv")
    parser.add_argument("--diversity", type=Path, help="instead, write the observer-diversity check here")
    args = parser.parse_args()
    if args.diversity:
        result = diversity(12)
        args.diversity.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        return
    tasks = [(f, e, p, r) for f in ("v2", "smooth") for e in (1, 2, 3) for p in ("random", "state")
             for r in range(args.replicates)]
    with ProcessPoolExecutor(args.workers, initializer=init) as pool:
        results = list(pool.map(run_one, tasks, chunksize=2))
    table = summarise(results)
    with open(args.table, "w", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=list(table[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(table)
    for row in table:
        print(row["family"], row["stratum"], row["phase"], row["extractor"],
              "eff", row["onset_effective_coverage"], row["end_effective_coverage"],
              "cond", row["onset_conditional_coverage"], row["end_conditional_coverage"],
              "unconf", row["unconfirmed_rate"], "w", row["onset_mean_width_d"], row["end_mean_width_d"],
              "unsafe/yr", row["causal_unsafe_per_year"], "miss", row["causal_missing_rate"],
              "prem", row["causal_premature_rate"])


if __name__ == "__main__":
    main()
