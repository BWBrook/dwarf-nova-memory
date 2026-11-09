"""Recount R2a clock populations from hashed saved features; no fits or scores."""

import argparse
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output exists; preserve previous check")
    receipt = json.loads((args.features / "receipt.json").read_text())
    inputs = {}
    ledgers = {}
    for name in ("df", "point_original", "point_at_df", "df_schedule_audit"):
        filename = name + "-unreleased.json"
        raw = (args.features / filename).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != receipt["output_sha256"][filename]:
            raise ValueError("saved feature hash differs: " + name)
        inputs[filename] = digest
        ledgers[name] = json.loads(raw)
    stop = date(2018, 1, 1).toordinal() + 1721424.5
    if any(row["issue_time"] >= stop for name in ("df", "point_original", "point_at_df")
           for row in ledgers[name]):
        raise ValueError("saved feature lies outside the opened period")
    result = {"scope": "gain-free recount of saved clock features; no model imports",
              "input_sha256": inputs, "periods": {}}
    for period, years in {"development": (1910, 1960), "evaluation": (1960, 2018)}.items():
        lo, hi = [date(y, 1, 1).toordinal() + 1721424.5 for y in years]
        selected = {name: [row for row in ledgers[name] if lo <= row["issue_time"] < hi]
                    for name in ("df", "point_original", "point_at_df")}
        left = {row["emission_index"]: row for row in selected["df"]}
        right = {row["emission_index"]: row for row in selected["point_at_df"]}
        if left.keys() != right.keys():
            raise ValueError("clocks have different matched issuances")
        markable = lambda row: (row["clock_anchor"] is not None
                                and row["previous_gap"] is not None
                                and row["mark"] is not None)
        delays = [row["issue_delay_days"] for row in selected["df"]]
        schedule = [row for row in ledgers["df_schedule_audit"]
                    if lo <= row["original_issue_time"] < hi]
        result["periods"][period] = {
            "original_point_issues": len(selected["point_original"]),
            "matched_issues": len(left),
            "DF_anchor_gap_mark": sum(map(markable, left.values())),
            "point_anchor_gap_mark": sum(map(markable, right.values())),
            "common_anchor_gap_mark": sum(markable(left[k]) and markable(right[k]) for k in left),
            "DF_only_markable": sum(markable(left[k]) and not markable(right[k]) for k in left),
            "point_only_markable": sum(markable(right[k]) and not markable(left[k]) for k in left),
            "median_delay_days": statistics.median(delays),
            "maximum_delay_days": max(delays),
            "scheduling_counts_by_original_issue": dict(Counter(row["status"] for row in schedule)),
            "anchor_mismatches": sum(row.get("scheduled_minus_x5_anchor_days") not in (None, 0)
                                     for row in left.values())}
    result["checker_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"status": "completed", "output": str(args.output)}))


if __name__ == "__main__":
    main()
