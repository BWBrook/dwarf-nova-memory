"""Claude's review of G3a: where the frozen DF chain loses cycles, and the visual-record ceiling.

Gain-free and development-only. Reloads the retained pre-1990 native pages through the independent
checker's audited loader, reruns the frozen DF feature/outcome chain, and writes only aggregate counts:
the sequential attrition, single-gate relaxations, decade yields and the SS Aur long-run location
relative to the record. No mark is related to any gap; no fit, score or coefficient is computed.

    uv run --frozen --extra analysis python scripts/g3a_claude_review_checks.py \
        > data/provenance/g3a_claude_review/checks.json
"""

from __future__ import annotations

from collections import Counter
from datetime import date
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.extract import MIN_QUIET_NIGHTS, _nights, _runs, visits
from dnmem.extract_x3 import SPLIT_GAP
from dnmem.extract_x4 import causal_confirmations, x4_episodes
from dnmem.extract_x5 import decisive_visits, x5_episodes
from dnmem.g3a_qualification import morphology_screen
from dnmem.r2b_features import decoupled_schedule, decisive_feature
from dnmem.r2b_scoring import outcome_evidence

spec = importlib.util.spec_from_file_location("g3a_check", ROOT / "scripts" / "check_g3a_execution.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)

STOP = check.STOP
RAW = ROOT / "data" / "raw" / "g3a_20261110_d827313"
DETAILS = ROOT / "data" / "provenance" / "g3a_20261110" / "details.json"


def jd(year):
    return date(year, 1, 1).toordinal() + 1721424.5


DECADES = [(y, jd(y), jd(y + 10) if y < 1980 else STOP) for y in (1940, 1950, 1960, 1970, 1980)]


def decade_of(t):
    for y, a, b in DECADES:
        if a <= t < b:
            return str(y)
    return "pre1940"


def attrition(rows, threshold):
    visits_at_cutoff = [v for v in decisive_visits(rows, threshold, 1.) if v["available_at"] <= STOP]
    support_ids = {i for v in visits_at_cutoff for i in v["ids"]}
    closed = [r for r in rows if r["obsID"] in support_ids]
    episodes = x5_episodes(closed, threshold, 1., episodes=x4_episodes(closed, threshold))
    confirmed = [e for e in episodes if e["confirmed_event"]]
    emissions = causal_confirmations(closed, threshold)
    observed = decisive_visits(closed, threshold, 1.)
    schedule = decoupled_schedule(emissions, observed, STOP)
    sched = {s["emission_index"]: s for s in schedule}
    emis = {e["emission_index"]: e for e in emissions}
    times = [float(r["JD"]) for r in closed]
    features = [decisive_feature(closed, times, emis[s["emission_index"]], s, sched, emis, threshold)
                for s in schedule if s["status"] == "scheduled"]
    evidence = {e["emission_index"]: e for e in outcome_evidence(closed, features, stop=STOP, threshold=threshold)}

    status, prev_state, outcome_kind = Counter(), Counter(), Counter()
    seq = Counter()
    relax = Counter()
    by_decade = {k: Counter() for k in ["pre1940"] + [str(y) for y, _, _ in DECADES]}
    marks, gaps_covered, fade_delay, onset_width = [], [], [], []
    for f in features:
        issue = f["issue_time"]
        ev = evidence[f["emission_index"]]
        clock = f.get("clock_anchor") is not None
        gap = f.get("previous_gap")
        has_gap = gap is not None and math.isfinite(float(gap)) and float(gap) > 0
        covered = has_gap and f.get("previous_gap_covered") is True
        mark = f.get("mark")
        has_mark = mark is not None and math.isfinite(float(mark)) and float(mark) > 0
        if ev["kind"] == "interval":
            usable = True
        elif ev["kind"] == "right_censored":
            usable = ev["censor_at"] > issue
        else:
            usable = False
        status[f.get("status", "unknown")] += 1
        if clock:
            sc = sched[f["emission_index"]]
            fade_delay.append(sc["anchor"] - sc["original_last_bright_at"])
        if ev["kind"] == "interval":
            onset_width.append(ev["onset_hi"] - ev["onset_lo"])
        outcome_kind[ev["kind"] if usable or ev["kind"] == "excluded" else "zero_exposure"] += 1
        if clock:
            hist = f.get("gap_history") or []
            prev_state["empty_history" if not hist else hist[-1]["reason"]] += 1
        seq["scheduled"] += 1
        seq["clock"] += clock
        seq["clock_prevcovered"] += clock and covered
        seq["clock_prevcovered_mark"] += clock and covered and has_mark
        seq["supported"] += clock and covered and has_mark and usable
        relax["without_previous_gap_coverage"] += clock and has_mark and usable
        relax["without_any_previous_gap"] += clock and has_mark and usable
        relax["without_two_decisive_bright_mark"] += clock and covered and usable
        relax["without_previous_gap_or_mark"] += clock and usable
        relax["clock_and_outcome_ceiling"] += clock and usable
        d = by_decade[decade_of(issue)]
        d["scheduled"] += 1
        d["supported"] += clock and covered and has_mark and usable
        d["clock_and_outcome"] += clock and usable
        if clock and covered and has_mark and usable:
            marks.append(float(mark))
            gaps_covered.append(float(gap))
    conf_decade = Counter(decade_of(float(e["peak_t"])) for e in confirmed)
    return dict(confirmed=len(confirmed), confirmed_by_decade=dict(conf_decade),
                feature_status=dict(status), previous_gap_state_given_clock=dict(prev_state),
                outcome_kind=dict(outcome_kind), sequential=dict(seq), single_gate_relaxations=dict(relax),
                by_decade={k: dict(v) for k, v in by_decade.items() if v},
                supported_mark_quantiles=[float(q) for q in np.quantile(marks, [.1, .5, .9])] if marks else None,
                fade_confirmation_delay_quantiles=[float(q) for q in np.quantile(fade_delay, [.1, .5, .9])]
                if fade_delay else None,
                onset_window_width_quantiles=[float(q) for q in np.quantile(onset_width, [.1, .5, .9])]
                if onset_width else None,
                supported_previous_gap_quantiles=[float(q) for q in np.quantile(gaps_covered, [.1, .5, .9])]
                if gaps_covered else None)


def long_run_context(rows, threshold):
    """Locate the screen's longest supported run and describe its contents in aggregate."""
    screen = morphology_screen(rows, threshold)
    votes = visits(rows, threshold)
    nights = _nights(votes)
    labels = {}
    for key, own in nights.items():
        b = sum(v["cls"] == "B" for v in own)
        labels[key] = "B" if 2 * b > len(own) else "F" if 2 * b < len(own) else "M"
    keys = sorted(nights)
    runs = [(run, split) for run, split in _runs(keys, lambda k: labels[k] != "F", SPLIT_GAP)
            if any(labels[k] == "B" for k in run)]
    merged = []
    for run, split in runs:
        if merged and not split and run[0] - merged[-1][0][-1] <= MIN_QUIET_NIGHTS:
            earlier, previous_split = merged.pop()
            run = earlier + [k for k in keys if earlier[-1] < k < run[0]] + run
            split = previous_split
        merged.append((run, split))
    best = None
    for run, _ in merged:
        own = sorted((v for k in run for v in nights[k]), key=lambda v: v["t"])
        bright = [v for v in own if v["cls"] == "B"]
        first, last = bright[0]["t"], bright[-1]["t"]
        times = sorted({v["t"] for v in own if first <= v["t"] <= last})
        hole = max((b - a for a, b in zip(times, times[1:])), default=0.)
        if (len({math.floor(v["t"]) for v in bright}) >= 10 and len({v["observer"] for v in bright}) >= 2
                and hole <= 7. and (best is None or last - first > best[0])):
            best = (last - first, first, last, own)
    span, first, last, own = best
    inside = [v for v in own if first <= v["t"] <= last]
    pos = [v["value"] for v in inside if v["value"] is not None]
    decisive_bright_nights = sorted({math.floor(v["t"]) for v in inside
                                     if v["value"] is not None and v["value"] <= threshold - 1.})
    clusters = 0
    for a, b in zip([None] + decisive_bright_nights, decisive_bright_nights):
        clusters += a is None or b - a > 7
    year = date.fromordinal(int(first - 1721424.5)).year
    quiescent_pos = [v["value"] for v in votes if v["value"] is not None and v["value"] > threshold]
    return dict(screen={k: screen[k] for k in ("longest_supported_bright_span_days", "runs_at_least_40_days",
                                               "runs_at_least_60_days", "supported_runs")},
                run_span_days=span, run_start_year=year,
                run_votes=len(inside), run_bright_votes=sum(v["cls"] == "B" for v in inside),
                run_faint_votes=sum(v["cls"] == "F" for v in inside),
                run_observers=len({v["observer"] for v in inside}),
                run_positive_quantiles_10_50_90=[float(q) for q in np.quantile(pos, [.1, .5, .9])],
                run_fraction_positive_within_1mag_brighter_than_threshold=float(np.mean(
                    [threshold - 1. < p <= threshold for p in pos])),
                run_decisive_bright_nights=len(decisive_bright_nights),
                run_decisive_bright_clusters_split_7d=clusters,
                record_faint_positive_median=float(np.median(quiescent_pos)) if quiescent_pos else None)


def six_star_recount():
    """Hash-checked recount of the frozen six-star supplement (C69) with the R2d review counter."""
    import hashlib
    sys.path.insert(0, str(ROOT / "scripts"))
    import r2d_claude_review_checks as r2d
    summary = json.loads((ROOT / "data/provenance/g3a_preparation/six-star-summary.json").read_text())
    out = {}
    for case in summary["cases"]:
        path = ROOT / "outputs/g3a_sixstar_d827313" / f"{case['case']}-trials.jsonl"
        stats, _ = r2d.case_stats(path)
        out[case["case"]] = dict(
            hash_matches=hashlib.sha256(path.read_bytes()).hexdigest() == case["trials_sha256"],
            passed=stats["passed"], star_score=stats["star"]["score"], star_gain=stats["star"]["gain"],
            gain_without_score_star=stats["star"]["gain_without_score"]["k"],
            gain_without_score_halves=stats["halves"]["gain_without_score"]["k"],
            counts_match_summary=(stats["star"]["gain"]["k"] == case["methods"]["star-gain"]["rejections"]
                                  and stats["star"]["score"]["k"] == case["methods"]["star-score"]["rejections"]))
    return out


def ceilings(stars, cyg, frozen_1980s):
    conf80 = sum(r["confirmed_by_decade"].get("1980", 0) for r in stars.values())
    tiers = {"frozen_rules": frozen_1980s,
             "ordinary_route_rerun": sum(r["by_decade"].get("1980", {}).get("supported", 0) for r in stars.values()),
             "without_history_and_mark": sum(r["by_decade"].get("1980", {}).get("clock_and_outcome", 0)
                                             for r in stars.values()),
             "every_confirmed_outburst": conf80}
    out = {"confirmed_1980s": conf80, "tiers_1980s": tiers,
           "projection_28y": {k: v * 2.8 for k, v in tiers.items()},
           "projection_36y": {k: v * 3.6 for k, v in tiers.items()},
           "conversion_needed_for_1100_36y": 1100 / 3.6 / conf80,
           "conversion_needed_for_1100_28y": 1100 / 2.8 / conf80,
           "conversion_1980s": {k: v / conf80 for k, v in tiers.items()},
           "stars_at_least_40_without_history_and_mark": sorted(
               n for n, r in stars.items() if r["single_gate_relaxations"]["clock_and_outcome_ceiling"] >= 40),
           "stars_with_fewer_than_40_confirmed_outbursts_in_whole_record": sorted(
               n for n, r in stars.items() if r["confirmed"] < 40)}
    c80 = cyg["by_decade"]["1980"]
    out["ss_cyg_1980s"] = {"confirmed": cyg["confirmed_by_decade"]["1980"], "supported": c80["supported"],
                           "conversion": c80["supported"] / cyg["confirmed_by_decade"]["1980"]}
    out["best_candidates_1980s_conversion"] = {
        n: stars[n]["by_decade"]["1980"]["supported"] / stars[n]["confirmed_by_decade"]["1980"]
        for n in ("SS Aur", "U Gem", "UU Aql", "RU Peg", "X Leo")}
    return out


def main():
    details = {s["name"]: s for s in json.loads(DETAILS.read_text())["stars"]}
    config = json.loads((ROOT / "configs" / "g3a_feasibility.json").read_text())
    audit = check.Audit()
    out = {"scope": "gain-free development-only diagnostics on retained pre-1990 pages; no mark-gap relation",
           "eclipse_holds_note": "U Gem/IP Peg here use the ordinary raw-report route, not their frozen derived streams",
           "stars": {}}
    for star in config["stars"]:
        name = star["name"]
        expected = details[name]
        rows, _ = check.acquire_audit(audit, RAW, star, expected)
        rows = [r for r in rows if float(r["JD"]) < STOP]
        res = attrition(rows, star["threshold"])
        if not star["eclipsing_hold"]:
            res["matches_frozen_supported"] = res["sequential"]["supported"] == expected["df_outcome_supported_marked"]
        if name == "SS Aur":
            res["morphology"] = long_run_context(rows, star["threshold"])
        out["stars"][name] = res
    cyg = sorted((r for r in json.loads((ROOT / "outputs/r1_censor_audit/validated-rows.json").read_text())
                  if r["band"] == "Vis." and r["val"] == "V" and float(r["JD"]) < STOP),
                 key=lambda r: (float(r["JD"]), r["obsID"]))
    out["ss_cyg_same_chain_reference"] = attrition(cyg, 10.0)
    out["ss_cyg_same_chain_reference"]["note"] = ("already-opened SS Cyg record, same pre-1990 cutoff, "
                                                  "frozen threshold 10.0 and margin 1.0; counts only")
    tot = Counter()
    for name, r in out["stars"].items():
        for k, v in r["sequential"].items():
            tot["seq_" + k] += v
        for k, v in r["single_gate_relaxations"].items():
            tot["relax_" + k] += v
        tot["confirmed"] += r["confirmed"]
        for k, v in r["by_decade"].get("1980", {}).items():
            tot["1980s_" + k] += v
    out["totals"] = dict(tot)
    frozen80 = sum(s["supported_last_decade_count"] for s in details.values())
    out["ceilings"] = ceilings(out["stars"], out["ss_cyg_same_chain_reference"], frozen80)
    out["six_star_recount"] = six_star_recount()
    out["audit_failures"] = audit.failures
    json.dump(out, sys.stdout, indent=1, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
