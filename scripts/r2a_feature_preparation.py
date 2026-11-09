#!/usr/bin/env python3
"""Prepare immutable prefix-only R2 feature ledgers; no model fits or scores."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.r2_features import prepare_feature_ledgers

STOP = 2458119.5
FROZEN_PATHS = ("docs/protocols/r2-design-v1.md", "src/dnmem/r2_features.py",
                "scripts/r2a_feature_preparation.py", "tests/test_r2_features.py",
                "src/dnmem/extract_x5.py")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")


def counts(features):
    slots = [entry for feature in features for entry in feature["gap_history"]]
    result = {"features": len(features), "status": dict(Counter(f["status"] for f in features)),
              "anchor_available": sum(f["clock_anchor"] is not None for f in features),
              "mark_available": sum(f["mark"] is not None for f in features),
              "previous_gap_available": sum(f["previous_gap"] is not None for f in features),
              "history_slots": len(slots), "history_missing_slots": sum(h["log_gap"] is None for h in slots),
              "history_reasons": dict(Counter(h["reason"] for h in slots)),
              "event_eligible": sum(f["event_eligible"] for f in features),
              "flux_proxy_status": dict(Counter(f["flux_proxy"]["status"] for f in features)),
              "flux_proxy_available": sum(f["flux_proxy"]["value_threshold_flux_days"] is not None for f in features)}
    if features and "frozen_point_reference" in features[0]:
        result["frozen_previous_gap_available"] = sum(
            f["frozen_point_reference"]["previous_gap"] is not None
            and f["frozen_point_reference"]["previous_gap_covered"] is True for f in features)
        result["frozen_usable_gap_now_unavailable"] = sum(
            f["frozen_point_reference"]["previous_gap"] is not None
            and f["frozen_point_reference"]["previous_gap_covered"] is True
            and f["previous_gap"] is None for f in features)
    return result


def summary(ledgers):
    issued = ledgers["df"]
    delays = [f["issue_delay_days"] for f in issued]
    mismatches = [f["scheduled_minus_x5_anchor_days"] for f in issued
                  if f.get("scheduled_minus_x5_anchor_days") is not None]
    result = {"label": "R2a gain-free prefix-feature preparation; no fitting, gain or correlation",
              "all_opened_record": {name: counts(ledgers[name]) for name in ("point_original", "df", "point_at_df")},
              "df_scheduling_status": dict(Counter(r["status"] for r in ledgers["df_schedule_audit"])),
              "df_issue_delay_days": {"n": len(delays), "positive": sum(d > 0 for d in delays),
                                       "median": statistics.median(delays) if delays else None,
                                       "maximum": max(delays, default=None)},
              "scheduled_current_vs_x5_first_postpeak_anchor": {
                  "comparable": len(mismatches), "different": sum(x != 0 for x in mismatches),
                  "maximum_absolute_days": max((abs(x) for x in mismatches), default=None)},
              "periods": {},
              "limitations": [
                  "Point clocks use full raw prefixes; DF uses visits closed by actual issue.",
                  "Scheduled current DF anchor follows the after-last-bright policy; past X5 anchors use first post-peak decisive faint visits.",
                  "Histories are reconstructed as of each issue with consecutive report-candidate slots, not physical event counts or earliest historical values.",
                  "State filters must rebuild once per feature and must not update again from the separately repeated previous_gap field.",
                  "No fitted-end estimate schedules or associates DF; observation and landmark-selection pathways remain.",
                  "A scheduled DF row with failed raw association remains an explicit common fallback."]}
    result["limitations"].append(
        "The flux proxy is observed bright-span threshold excess with observer-night medians, not complete outburst/quiescent-subtracted/bolometric fluence.")
    for name, (begin, end) in {"development_1910_1959": (date(1910, 1, 1), date(1960, 1, 1)),
                              "opened_evaluation_1960_2017": (date(1960, 1, 1), date(2018, 1, 1))}.items():
        lo, hi = begin.toordinal() + 1721424.5, end.toordinal() + 1721424.5
        result["periods"][name] = {clock: counts([f for f in ledgers[clock] if lo <= f["issue_time"] < hi])
                                    for clock in ("point_original", "df", "point_at_df")}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=ROOT / "outputs/r1_censor_audit")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--freeze-commit", required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output directory exists; preserve prior ledgers")
    relative = args.output.resolve().relative_to(ROOT)
    if subprocess.run(["git", "check-ignore", "-q", str(relative / "df-unreleased.json")], cwd=ROOT).returncode:
        parser.error("feature ledgers must be ignored by Git")
    for source in FROZEN_PATHS:
        frozen = subprocess.check_output(["git", "show", args.freeze_commit + ":" + source], cwd=ROOT)
        if frozen != (ROOT / source).read_bytes():
            parser.error(source + " differs from the declared freeze")
    cache_receipt = json.loads((args.cache / "private-cache-receipt.json").read_text())
    if cache_receipt["stop_jd_exclusive"] != STOP:
        raise ValueError("cache date boundary differs from the authorized record")
    for name, metadata in cache_receipt["files"].items():
        if digest(args.cache / name) != metadata["sha256"]:
            raise ValueError("cache hash mismatch: " + name)
    for key, source in (("extractor_sha256", "src/dnmem/extract_x4.py"), ("visit_builder_sha256", "src/dnmem/extract.py")):
        if digest(ROOT / source) != cache_receipt[key]:
            raise ValueError("frozen source differs from cache: " + source)
    rows = json.loads((args.cache / "validated-rows.json").read_text())
    if any(float(r["JD"]) >= STOP or r["band"] != "Vis." or r["val"] != "V" for r in rows):
        raise ValueError("cache violates authorized visual/time scope")
    args.output.mkdir(parents=True)
    receipt = {
        "status": "running", "freeze_commit": args.freeze_commit,
        "cache_receipt_sha256": digest(args.cache / "private-cache-receipt.json"),
        "source_sha256": {name: digest(ROOT / name) for name in FROZEN_PATHS},
        "scope": "already opened through2017 record; no fit, score, correlation or archive request"}
    write(args.output / "receipt.json", receipt)
    try:
        ledgers = prepare_feature_ledgers(rows, stop=STOP)
        result = summary(ledgers)
    except Exception as exc:
        receipt.update(status="failed", error_type=type(exc).__name__, error=str(exc))
        write(args.output / "receipt.json", receipt)
        raise
    for name, ledger in ledgers.items():
        write(args.output / (name + "-unreleased.json"), ledger)
    write(args.output / "summary.json", result)
    receipt.update(status="completed", output_sha256={p.name: digest(p) for p in args.output.iterdir() if p.name != "receipt.json"})
    write(args.output / "receipt.json", receipt)
    print(json.dumps({"status": "gain-free feature preparation complete",
                      "point_original": len(ledgers["point_original"]), "df": len(ledgers["df"]),
                      "point_at_df": len(ledgers["point_at_df"])}))


if __name__ == "__main__":
    main()
