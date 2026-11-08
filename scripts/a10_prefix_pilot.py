#!/usr/bin/env python3
"""A10 prefix-causal predictor pilot: what causality costs, on open-era and synthetic inputs.

Real 1910-1959 rows: prefix-versus-retrospective boundary differences, confirmation
lag and outcome-evidence status counts only. No real duration-gap association is
computed or written. Synthetic v2-phase histories (development seeds
`a10-claude-dev-*`): the same diagnostics plus duration-gap correlation retention
for true, retrospective and prefix durations.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import math
from pathlib import Path
import statistics as st
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.extract_x4 import x4_episodes
from dnmem.prefix_features import forecast_ledger, outcome_evidence

J1910, J1960 = 2418672.5, 2436934.5
BASE = "a10-claude-dev-20261108"
ERAS = ("1910_1929", "1930_1949", "1950_1959")
STATE = {}


def q(values, p):
    v = sorted(values)
    return v[min(len(v) - 1, int(p * len(v)))] if v else None


def summary(values):
    v = [x for x in values if x is not None]
    return {"n": len(v), "median": round(q(v, .5), 3), "p10": round(q(v, .1), 3), "p90": round(q(v, .9), 3),
            "mean_abs": round(st.fmean(abs(x) for x in v), 3)} if v else {"n": 0}


def retro_match(episode_onset, retro):
    return min(retro, key=lambda e: abs(e["onset_t"] - episode_onset), default=None) if episode_onset else None


def diagnose(rows, start, stop):
    ledger = forecast_ledger(rows, start=start, stop=stop)
    evidence = outcome_evidence(rows, ledger, stop=stop)
    retro = [e for e in x4_episodes(rows) if e["confirmed_event"] and e["onset_t"] is not None
             and e["end_t"] is not None]
    out = []
    for f, ev in zip(ledger, evidence):
        r = retro_match(f["onset_t"], retro)
        same = r is not None and abs(r["onset_t"] - f["onset_t"]) < 1.0
        out.append({"forecast": f, "evidence": ev, "retro": r if same else None})
    return out


def costs(items, years):
    found = [i for i in items if i["forecast"]["duration"] is not None]
    paired = [i for i in found if i["retro"] is not None]
    width = lambda e, k: e[f"{k}_hi"] - e[f"{k}_lo"] if e[f"{k}_hi"] is not None and e[f"{k}_lo"] is not None else None
    reasons = {}
    for i in items:
        key = i["evidence"]["reason"]
        reasons[key] = reasons.get(key, 0) + 1
    return {"forecasts": len(items), "forecasts_per_year": round(len(items) / years, 3),
            "with_prefix_duration": len(found), "without_prefix_episode": sum(not i["forecast"]["episode_found"] for i in items),
            "matched_to_retrospective_episode": len(paired),
            "repeat_of_previous": sum(i["forecast"]["repeat_of_previous"] for i in items),
            "prefix_end_fit": sum(i["forecast"]["end_method"] == "fit" for i in found),
            "duration_prefix_minus_retro_d": summary([i["forecast"]["duration"] - (i["retro"]["end_t"] - i["retro"]["onset_t"]) for i in paired]),
            "end_prefix_minus_retro_d": summary([i["forecast"]["end_t"] - i["retro"]["end_t"] for i in paired]),
            "end_width_prefix_d": summary([width(i["forecast"], "end") for i in paired]),
            "end_width_retro_d": summary([width(i["retro"], "end") for i in paired]),
            "end_fit_points_lost": summary([i["retro"]["n_end_fit"] - i["forecast"]["n_end_fit"] for i in paired]),
            "age_at_issue_d": summary([i["forecast"]["age_at_issue"] for i in found]),
            "previous_gap_available_covered": sum(bool(i["forecast"]["previous_gap_covered"]) for i in items),
            "outcome_reasons": reasons}


def pearson(x, y):
    mx, my = st.fmean(x), st.fmean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy / math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))


def partial(x, y, z):
    rxy, rxz, ryz = pearson(x, y), pearson(x, z), pearson(y, z)
    return (rxy - rxz * ryz) / math.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))


def init():
    STATE["inputs"] = json.loads((ROOT / "outputs/a04i_inputs_frozen_20261108/inputs.json").read_text())
    STATE["config"] = json.loads((ROOT / "configs/a04i_selected.json").read_text())["v2-phase"]


def synthetic(task):
    from dnmem.joint_benchmark import generate_observations
    from dnmem.x4_benchmark import seed_for
    process, era, replicate = task
    stratum = next(s for s in STATE["inputs"]["strata"] if s["stratum"] == era)
    seed = seed_for(BASE, process, era, replicate)
    rows, history, generator, _, _ = generate_observations(STATE["inputs"], STATE["config"], stratum, seed, process)
    start, stop = float(stratum["start"]), float(stratum["stop"])
    truth = sorted(generator.truth_catalogue(history, 10.0), key=lambda e: e["onset"])
    items = diagnose(rows, start, stop)
    records = []
    for i in items:
        f = i["forecast"]
        j = None
        if f["onset_t"] is not None and f["end_t"] is not None:
            overlaps = [(min(f["end_t"], e["end"]) - max(f["onset_t"], e["onset"]), k) for k, e in enumerate(truth)]
            best = max(overlaps, default=(0, None))
            j = best[1] if best[0] > 0 else None
        rec = {"duration_prefix": f["duration"], "previous_gap_prefix": f["previous_gap"] if f["previous_gap_covered"] else None,
               "duration_retro": (i["retro"]["end_t"] - i["retro"]["onset_t"]) if i["retro"] else None,
               "true_index": j, "repeat": f["repeat_of_previous"], "reason": i["evidence"]["reason"],
               "wait_observed": (i["evidence"]["onset_t"] - f["issue_time"]) if i["evidence"]["kind"] == "interval" else None}
        if j is not None and 0 < j < len(truth) - 1:
            e = truth[j]
            rec.update(duration_true=e["end"] - e["onset"], gap_true=truth[j + 1]["onset"] - e["end"],
                       previous_gap_true=e["onset"] - truth[j - 1]["end"], issue_minus_true_end=f["issue_time"] - e["end"])
        records.append(rec)
    return {"process": process, "era": era, "replicate": replicate, "years": (stop - start) / 365.25,
            "costs": costs(items, (stop - start) / 365.25), "records": records,
            "true_events": len(truth)}


def retention(records):
    use = [r for r in records if r.get("duration_true") and r["duration_prefix"] and r["duration_retro"]
           and r["duration_prefix"] > 0 and r["duration_retro"] > 0 and not r["repeat"]]
    lq = [math.log(r["gap_true"]) for r in use]
    out = {"forecasts": len(use)}
    for k in ("true", "retro", "prefix"):
        out[f"r_log_duration_{k}_vs_log_gap_true"] = round(pearson([math.log(r[f"duration_{k}"]) for r in use], lq), 4)
    part = [r for r in use if r["previous_gap_prefix"] and r["previous_gap_prefix"] > 0]
    lqp = [math.log(r["gap_true"]) for r in part]
    for k in ("true", "prefix"):
        out[f"partial_r_{k}_given_previous_gap"] = round(partial(
            [math.log(r[f"duration_{k}"]) for r in part], lqp,
            [math.log(r["previous_gap_true"] if k == "true" else r["previous_gap_prefix"]) for r in part]), 4)
    out["partial_forecasts"] = len(part)
    lag = [r["issue_minus_true_end"] for r in use]
    out["issue_minus_true_end_d"] = summary(lag)
    out["r_log_duration_true_vs_lag"] = round(pearson([math.log(r["duration_true"]) for r in use], lag), 4)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=12)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--output", type=Path, default=ROOT / "data/simulations/a10_prefix_pilot_20261108.json")
    args = parser.parse_args()
    from dnmem.coverage import combine_acquisitions
    rows, _ = combine_acquisitions(sorted((ROOT / "data/raw").glob("aavso_ss_cyg_*/native.xml")))
    rows = [r for r in rows if float(r["JD"]) < J1960]
    result = {"definition": "dnmem.prefix_features a10-prefix-v1, X4 at 10.0, lookback 400 d, C1/7 d, latency 0",
              "seed_base": BASE,
              "real_1910_1959": {"note": "boundary, lag and evidence-status diagnostics only; no duration-gap association",
                                 **costs(diagnose(rows, J1910, J1960), (J1960 - J1910) / 365.25)}}
    init()
    tasks = [(p, e, r) for p in ("alternative", "null") for e in ERAS for r in range(args.replicates)]
    with ProcessPoolExecutor(args.workers, initializer=init) as pool:
        done = list(pool.map(synthetic, tasks))
    for process in ("alternative", "null"):
        runs = [d for d in done if d["process"] == process]
        records = [r for d in runs for r in d["records"]]
        years = sum(d["years"] for d in runs)
        unmatched = sum(r["true_index"] is None for r in records)
        merged = {}
        for era in ERAS:
            era_items = [d for d in runs if d["era"] == era]
            merged[era] = {"histories": len(era_items),
                           "forecasts_per_year": round(sum(d["costs"]["forecasts"] for d in era_items) / sum(d["years"] for d in era_items), 3),
                           "true_events_per_year": round(sum(d["true_events"] for d in era_items) / sum(d["years"] for d in era_items), 3),
                           "duration_prefix_minus_retro_d": summary([
                               r["duration_prefix"] - r["duration_retro"] for d in era_items for r in d["records"]
                               if r["duration_prefix"] is not None and r["duration_retro"] is not None])}
        reasons = {}
        for r in records:
            reasons[r["reason"]] = reasons.get(r["reason"], 0) + 1
        result[f"synthetic_v2_phase_{process}"] = {
            "histories": len(runs), "forecasts": len(records), "forecasts_without_true_event_per_year": round(unmatched / years, 4),
            "outcome_reasons": reasons, "by_era": merged, "retention": retention(records)}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
