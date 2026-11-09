#!/usr/bin/env python3
"""Gain-free X5 preparation from already opened, receipt-bound SS Cyg caches."""

from __future__ import annotations

import argparse
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.extract_x5 import decisive_visits, x5_episodes

STOP = 2458119.5
PROTOCOL = "docs/protocols/r2-design-v1.md"
FROZEN_PATHS = (PROTOCOL, "src/dnmem/extract_x5.py", "scripts/r2a_observation_diagnostics.py",
                "tests/test_extract_x5.py")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")


def distribution(values):
    values = sorted(values)
    if not values:
        return {"n": 0}
    def quantile(probability):
        x = (len(values) - 1) * probability
        lo, hi = math.floor(x), math.ceil(x)
        return values[lo] + (x - lo) * (values[hi] - values[lo])
    return {"n": len(values), "median": statistics.median(values), "p25": quantile(.25),
            "p75": quantile(.75), "p90": quantile(.90), "maximum": max(values),
            "share_le_2_days": sum(x <= 2 for x in values) / len(values),
            "share_le_5_days": sum(x <= 5 for x in values) / len(values)}


def episode_summary(episodes):
    widths = [e["onset_report_hi"] - e["onset_report_lo"] for e in episodes if e["onset_report_available"]]
    representative = [e["onset_report_hi_rep"] - e["onset_report_lo_rep"] for e in episodes if e["onset_report_available"]]
    flags = Counter(flag for e in episodes for flag in e["onset_flags"])
    return {"episodes": len(episodes), "onset_status": dict(Counter(e["onset_status"] for e in episodes)),
            "onset_flags": dict(flags), "onset_available": len(widths),
            "onset_eligible": sum(e["onset_report_eligible"] for e in episodes),
            "raw_support_width_days": distribution(widths),
            "representative_width_days": distribution(representative),
            "end_status": dict(Counter(e["end_status"] for e in episodes)),
            "end_available": sum(e["end_report_available"] for e in episodes),
            "end_eligible": sum(e["end_report_eligible"] for e in episodes),
            "x4_point_outside_available_onset_window": sum(
                e["onset_t"] is not None and not e["onset_report_lo"] < e["onset_t"] <= e["onset_report_hi"]
                for e in episodes if e["onset_report_available"]),
            "rise_decisive_faint_after_bright_reports": sum(e["rise_decisive_faint_after_bright_count"] for e in episodes),
            "post_end_bright_before_next_peak_episodes": sum(e["post_end_decisive_bright_before_next_peak"] for e in episodes)}


def window_visit_diagnostics(episode, observed, times=None):
    if not episode["onset_report_available"]:
        return None
    lo, hi = episode["onset_report_lo_rep"], episode["onset_report_hi_rep"]
    times = [v["t"] for v in observed] if times is None else times
    before = observed[bisect_left(times, lo - 5):bisect_left(times, lo)]
    inclusive = observed[bisect_right(times, lo):bisect_right(times, hi)]
    interior = observed[bisect_right(times, lo):bisect_left(times, hi)]
    threshold, margin = episode["x5_threshold"], episode["x5_margin"]
    near = [v for v in observed[bisect_right(times, episode["quiescence_at"]):bisect_left(times, hi)]
            if v["value"] is not None and threshold - margin < v["value"] <= threshold]
    gaps = [b["t"] - a["t"] for a, b in zip(before, before[1:])]
    positive = [g for g in gaps if g > 0]
    return {"width_days": hi - lo, "before_days": 5.0, "before_visits": len(before),
            "inside_including_upper_visits": len(inclusive), "strict_interior_visits": len(interior),
            "nondecisive_bright_to_upper_days": hi - near[0]["t"] if near else None,
            "background_positive_intervisit_gap_median": statistics.median(positive) if positive else None,
            "background_zero_intervisit_gaps": sum(g == 0 for g in gaps),
            "eligible": episode["onset_report_eligible"]}


def visit_rate_summary(records):
    if not records:
        return {"windows": 0}
    width = math.fsum(r["width_days"] for r in records)
    before = sum(r["before_visits"] for r in records) / (5 * len(records))
    inclusive = sum(r["inside_including_upper_visits"] for r in records) / width
    interior = sum(r["strict_interior_visits"] for r in records) / width
    return {"windows": len(records), "total_window_days": width,
            "background_observer_visits_per_day": before,
            "inside_including_upper_observer_visits_per_day": inclusive,
            "strict_interior_observer_visits_per_day": interior,
            "inclusive_to_background_rate_ratio": inclusive / before if before else None,
            "interior_to_background_rate_ratio": interior / before if before else None,
            "nondecisive_bright_to_upper_days": distribution([r["nondecisive_bright_to_upper_days"] for r in records
                                                             if r["nondecisive_bright_to_upper_days"] is not None]),
            "background_positive_intervisit_gap_medians": distribution([r["background_positive_intervisit_gap_median"] for r in records
                                                                        if r["background_positive_intervisit_gap_median"] is not None]),
            "background_zero_intervisit_gaps": sum(r["background_zero_intervisit_gaps"] for r in records)}


def contradiction_diagnostics(episodes, observed, separation=.5, phase_margin=3.0):
    phases = []
    for index, e in enumerate(episodes):
        if e["confirmed_event"] and e["onset_report_eligible"] and e["end_report_eligible"]:
            phases.append((e["onset_report_hi"] + phase_margin, e["end_report_lo"] - phase_margin, "plateau"))
        if e["confirmed_event"] and e["end_report_eligible"] and index + 1 < len(episodes):
            following = episodes[index + 1]
            if following["onset_report_eligible"]:
                phases.append((e["end_report_hi"] + phase_margin, following["onset_report_lo"] - phase_margin, "quiescence"))
    phases = sorted((a, b, name) for a, b, name in phases if a < b)
    indexed_phases = {}
    for name in ("plateau", "quiescence"):
        own = [(a, b) for a, b, kind in phases if kind == name]
        if any(left[1] > right[0] for left, right in zip(own, own[1:])):
            raise ValueError("clear-phase windows overlap")
        indexed_phases[name] = ([a for a, _ in own], [b for _, b in own])
    selected = [v for v in observed if v["decisive"] != "N"]
    times = [v["t"] for v in selected]
    counts = {name: Counter() for name in ("all", "plateau", "quiescence")}
    for v in selected:
        contradictory = any(w["observer"] != v["observer"] and w["decisive"] != v["decisive"]
                            for w in selected[bisect_left(times, v["t"] - separation):bisect_right(times, v["t"] + separation)])
        strata = ["all"]
        for name, (starts, stops) in indexed_phases.items():
            index = bisect_left(starts, v["t"]) - 1
            if index >= 0 and v["t"] < stops[index]:
                strata.append(name)
        for name in set(strata):
            counts[name]["decisive_visits"] += 1
            counts[name]["visits_with_opposite_other_observer"] += contradictory
    return {name: {"decisive_visits": c["decisive_visits"],
                   "visits_with_opposite_other_observer": c["visits_with_opposite_other_observer"],
                   "fraction": c["visits_with_opposite_other_observer"] / c["decisive_visits"] if c["decisive_visits"] else None}
            for name, c in counts.items()}


def diagnostics(episodes, observed):
    confirmed = [e for e in episodes if e["confirmed_event"]]
    by_decade = defaultdict(list)
    for e in confirmed:
        year = date.fromordinal(math.floor(e["peak_t"] - 1721424.5)).year
        by_decade[str(10 * (year // 10))].append(e)
    times = [v["t"] for v in observed]
    windows = [r for e in confirmed if (r := window_visit_diagnostics(e, observed, times)) is not None]
    return {"label": "R2a gain-free X5 report-window diagnostics; no score or fit",
            "all_candidates": episode_summary(episodes), "confirmed_candidates": episode_summary(confirmed),
            "confirmed_by_decade": {k: episode_summary(v) for k, v in sorted(by_decade.items())},
            "cadence_all_available": visit_rate_summary(windows),
            "cadence_eligible": visit_rate_summary([r for r in windows if r["eligible"]]),
            "decisive_cross_observer_contradictions": contradiction_diagnostics(episodes, observed),
            "limitations": [
                "Fainter-than limits are numerical magnitude lower bounds, not positive magnitudes.",
                "Report windows and raw visit supports do not prove latent-onset containment or event completeness.",
                "Contradiction fractions are descriptive visit fractions, not probabilities of failed brackets; no failed-bracket count is identified.",
                "Clear-phase strata require eligible neighbouring report windows and can underrepresent transition errors.",
                "Selected onset windows force an upper detection; inclusive and strict-interior cadence comparisons are both reported.",
                "Visit-rate contrasts and alert lags do not establish CAR or rule out unrecorded triggers.",
                "Post-end bright reports before the next peak can be the ordinary next rise, not a current-event recrossing.",
                "Calendar decades label native JD values; no photometric-time convention is converted."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=ROOT / "outputs/r1_censor_audit")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--freeze-commit", required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output directory exists; preserve previous diagnostics")
    relative = args.output.resolve().relative_to(ROOT)
    if subprocess.run(["git", "check-ignore", "-q", str(relative / "episodes-unreleased.json")], cwd=ROOT).returncode:
        parser.error("episode output must be ignored by Git")
    for name in FROZEN_PATHS:
        frozen = subprocess.check_output(["git", "show", args.freeze_commit + ":" + name], cwd=ROOT)
        if frozen != (ROOT / name).read_bytes():
            parser.error(name + " differs from the declared freeze")
    cache_receipt = json.loads((args.cache / "private-cache-receipt.json").read_text())
    if cache_receipt["stop_jd_exclusive"] != STOP:
        raise ValueError("cache date boundary differs from the authorized record")
    for name, meta in cache_receipt["files"].items():
        if digest(args.cache / name) != meta["sha256"]:
            raise ValueError("cache hash mismatch: " + name)
    for key, source in (("extractor_sha256", "src/dnmem/extract_x4.py"), ("visit_builder_sha256", "src/dnmem/extract.py")):
        if digest(ROOT / source) != cache_receipt[key]:
            raise ValueError("frozen source differs from cache: " + source)
    rows = json.loads((args.cache / "validated-rows.json").read_text())
    if any(float(r["JD"]) >= STOP or r["band"] != "Vis." or r["val"] != "V" for r in rows):
        raise ValueError("cache violates the opened visual/time scope")
    candidates = json.loads((args.cache / "all-x4-episodes.json").read_text())
    votes = json.loads((args.cache / "visits.json").read_text())
    episodes = x5_episodes(rows, episodes=candidates, votes=votes)
    observed = decisive_visits(rows, votes=votes)
    summary = diagnostics(episodes, observed)
    args.output.mkdir(parents=True)
    write(args.output / "episodes-unreleased.json", episodes)
    write(args.output / "summary.json", summary)
    receipt = {"freeze_commit": args.freeze_commit, "cache_receipt_sha256": digest(args.cache / "private-cache-receipt.json"),
               "source_sha256": {name: digest(ROOT / name) for name in FROZEN_PATHS},
               "output_sha256": {p.name: digest(p) for p in args.output.iterdir()},
               "scope": "already opened through2017 cache; no archive request, model fit or score"}
    write(args.output / "receipt.json", receipt)
    print(json.dumps({"status": "gain-free diagnostics complete", "confirmed_candidates": len([e for e in episodes if e["confirmed_event"]]),
                      "onset_available": summary["confirmed_candidates"]["onset_available"],
                      "onset_eligible": summary["confirmed_candidates"]["onset_eligible"]}))


if __name__ == "__main__":
    main()
