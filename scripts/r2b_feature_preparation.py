#!/usr/bin/env python3
"""Prepare R2b clock/control ledgers from the retained cache; no fits or scores."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.r2b_features import prepare_feature_ledgers

STOP = 2458119.5
FROZEN_PATHS = (
    "docs/protocols/r2b-execution-v1.md", "src/dnmem/r2b_features.py",
    "scripts/r2b_feature_preparation.py", "tests/test_r2b_features.py",
    "src/dnmem/r2_features.py", "src/dnmem/extract_x5.py", "src/dnmem/extract_x4.py",
    "src/dnmem/extract_x3.py", "src/dnmem/extract.py", "src/dnmem/prefix_features.py", "uv.lock")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")


def distribution(values):
    ordered = sorted(values)
    return {"n": len(ordered), "median": statistics.median(ordered) if ordered else None,
            "p90_order_statistic": ordered[int(.9 * len(ordered))] if ordered else None,
            "maximum": max(ordered, default=None)}


def counts(features):
    slots = [entry for feature in features for entry in feature["gap_history"]]
    result = {"features": len(features), "status": dict(Counter(f["status"] for f in features)),
              "anchor_available": sum(f["clock_anchor"] is not None for f in features),
              "mark_available": sum(f["mark"] is not None for f in features),
              "previous_gap_available": sum(f["previous_gap"] is not None for f in features),
              "anchor_gap_mark_available": sum(all(f[k] is not None for k in ("clock_anchor", "previous_gap", "mark"))
                                               for f in features),
              "history_slots": len(slots), "history_missing_slots": sum(h["log_gap"] is None for h in slots),
              "history_reasons": dict(Counter(h["reason"] for h in slots)),
              "event_eligible": sum(f["event_eligible"] for f in features),
              "flux_proxy_available": sum(f["flux_proxy"]["value_threshold_flux_days"] is not None for f in features),
              "rate_available": sum(f["observer_rate"]["value_per_day"] is not None for f in features),
              "cadence_end_days": distribution([f["cadence_end"]["value_days"] for f in features
                                                 if f["cadence_end"]["value_days"] is not None]),
              "cadence_on_days": distribution([f["cadence_on"]["value_days"] for f in features
                                                if f["cadence_on"]["value_days"] is not None])}
    if features and features[0]["clock"] == "decisive":
        comparable = [f for f in features if f.get("historical_clock_anchor") is not None]
        result.update(own_anchor_association=dict(Counter(f.get("own_scheduled_anchor_association", "fallback") for f in features)),
                      current_historical_anchor_comparable=len(comparable),
                      current_historical_anchor_mismatches=sum(f["clock_anchor"] != f["historical_clock_anchor"] for f in comparable),
                      issue_delay_days=distribution([f["issue_delay_days"] for f in features]))
    return result


def summary(ledgers):
    result = {"label": "R2b gain-free causal features; no fits, gains or correlations",
              "all_opened_record": {clock: counts(ledgers[clock]) for clock in ("point_original", "df", "point_at_df")},
              "schedule_status": dict(Counter(row["status"] for row in ledgers["df_schedule_audit"])),
              "periods": {},
              "limitations": [
                  "Historical DF gaps require unique raw-peak association to a previously scheduled emission; missing/ambiguous anchors remain missing slots.",
                  "Historical onsets and coverage are reconstructed as of each current issue, not claimed immutable values from the past issue.",
                  "The DF anchor is a scheduled observed faint support, not an estimated latent end.",
                  "Cadence gaps use raw positive estimates belonging to closed visits; numerical limits are not exact positive values.",
                  "Observer rate includes closed observer-night visits, including limits, inside the decisive-bright span. The span and denominator depend on the star.",
                  "Cadence gaps and the rate are sensitivity features, not proven bounds or pure negative controls.",
                  "The proxy integrates observed-span threshold excess; it is not complete outburst or bolometric fluence."]}
    for period, years in {"development_1910_1959": (1910, 1960), "evaluation_1960_2017": (1960, 2018)}.items():
        lo, hi = [date(year, 1, 1).toordinal() + 1721424.5 for year in years]
        selected = {clock: [f for f in ledgers[clock] if lo <= f["issue_time"] < hi]
                    for clock in ("point_original", "df", "point_at_df")}
        df = {f["emission_index"]: f for f in selected["df"]}
        point = {f["emission_index"]: f for f in selected["point_at_df"]}
        if df.keys() != point.keys():
            raise ValueError("matched period populations differ")
        usable = lambda row: all(row[k] is not None for k in ("clock_anchor", "previous_gap", "mark"))
        result["periods"][period] = {clock: counts(features) for clock, features in selected.items()}
        result["periods"][period]["joint_clocks_anchor_gap_mark"] = sum(usable(df[k]) and usable(point[k]) for k in df)
        schedule = [row for row in ledgers["df_schedule_audit"] if lo <= row["original_issue_time"] < hi]
        result["periods"][period]["schedule_status_by_original_issue"] = dict(Counter(row["status"] for row in schedule))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=ROOT / "outputs/r1_censor_audit")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--freeze-commit", required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output exists; preserve earlier preparations")
    relative = args.output.resolve().relative_to(ROOT)
    if subprocess.run(["git", "check-ignore", "-q", str(relative / "df-unreleased.json")], cwd=ROOT).returncode:
        parser.error("individual real features must be ignored by Git")
    for name in FROZEN_PATHS:
        frozen = subprocess.check_output(["git", "show", args.freeze_commit + ":" + name], cwd=ROOT)
        if frozen != (ROOT / name).read_bytes():
            parser.error(name + " differs from the declared freeze")
    cache_receipt = json.loads((args.cache / "private-cache-receipt.json").read_text())
    if cache_receipt["stop_jd_exclusive"] != STOP:
        raise ValueError("retained cache has a different date boundary")
    for name, metadata in cache_receipt["files"].items():
        if digest(args.cache / name) != metadata["sha256"]:
            raise ValueError("retained cache hash differs: " + name)
    for key, name in (("extractor_sha256", "src/dnmem/extract_x4.py"), ("visit_builder_sha256", "src/dnmem/extract.py")):
        if digest(ROOT / name) != cache_receipt[key]:
            raise ValueError("retained cache source differs: " + name)
    rows = json.loads((args.cache / "validated-rows.json").read_text())
    if any(float(r["JD"]) >= STOP or r["band"] != "Vis." or r["val"] != "V" for r in rows):
        raise ValueError("retained cache violates the authorized date/band scope")
    args.output.mkdir(parents=True)
    receipt = {"status": "running", "freeze_commit": args.freeze_commit,
               "cache_receipt_sha256": digest(args.cache / "private-cache-receipt.json"),
               "source_sha256": {name: digest(ROOT / name) for name in FROZEN_PATHS},
               "environment": {"python": sys.version, "platform": platform.platform(),
                               "numpy": importlib.metadata.version("numpy"), "scipy": importlib.metadata.version("scipy")},
               "scope": "retained SS Cyg through2017 only; gain-free; no archive request"}
    write(args.output / "receipt.json", receipt)
    try:
        ledgers = prepare_feature_ledgers(rows, stop=STOP)
        result = summary(ledgers)
        for name, ledger in ledgers.items():
            write(args.output / (name + "-unreleased.json"), ledger)
        write(args.output / "summary.json", result)
    except Exception as exc:
        receipt.update(status="failed", error_type=type(exc).__name__, error=str(exc))
        write(args.output / "receipt.json", receipt)
        raise
    receipt.update(status="completed", output_sha256={p.name: digest(p) for p in args.output.iterdir() if p.name != "receipt.json"})
    write(args.output / "receipt.json", receipt)
    print(json.dumps({"status": "gain-free R2b features complete", "point_original": len(ledgers["point_original"]),
                      "df": len(ledgers["df"]), "point_at_df": len(ledgers["point_at_df"])}))


if __name__ == "__main__":
    main()
