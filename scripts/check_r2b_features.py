"""Independent saved-vector invariants; no dnmem imports, models or score access."""

import argparse
from collections import Counter
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--features", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
SOURCE = args.features.resolve()
OUT = args.output.resolve()
OUT.mkdir(parents=True, exist_ok=False)
checks, errors, inputs = Counter(), [], {}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(name):
    raw = (SOURCE / name).read_bytes()
    inputs[name] = sha(raw)
    return json.loads(raw)


def require(condition, label, locator=""):
    checks[label] += 1
    if not condition:
        errors.append(label + (": " + locator if locator else ""))


def close(left, right, tol=1e-10):
    return left is not None and right is not None and math.isclose(left, right, rel_tol=0., abs_tol=tol)


def finite(value):
    return value is not None and math.isfinite(value)


receipt = read("receipt.json")
require(receipt["status"] == "completed", "completed feature receipt")
require(receipt["freeze_commit"] == "5fb69c6", "declared source freeze")
for name, expected in receipt["source_sha256"].items():
    frozen = subprocess.check_output(["git", "show", receipt["freeze_commit"] + ":" + name], cwd=ROOT)
    require(sha(frozen) == expected, "historical source hash", name)
    require(sha((ROOT / name).read_bytes()) == expected, "current source hash", name)
ledgers = {name: read(name + "-unreleased.json") for name in
           ("point_original", "df", "point_at_df", "df_schedule_audit")}
recorded_summary = read("summary.json")
for name, expected in receipt["output_sha256"].items():
    require(inputs[name] == expected, "saved output hash", name)
audit = {row["emission_index"]: row for row in ledgers["df_schedule_audit"]}
df = {row["emission_index"]: row for row in ledgers["df"]}
point = {row["emission_index"]: row for row in ledgers["point_at_df"]}
require(len(audit) == len(ledgers["df_schedule_audit"]), "unique audit IDs")
require(df.keys() == point.keys(), "DF matched-point identities")
require([(r["emission_index"], r["issue_time"]) for r in ledgers["df"]]
        == [(r["emission_index"], r["issue_time"]) for r in ledgers["point_at_df"]], "exact ordered issue pairing")
source_fallbacks = Counter()
scheduled_anchor_checks = 0
for clock in ("point_original", "df", "point_at_df"):
    rows = ledgers[clock]
    require(len({r["emission_index"] for r in rows}) == len(rows), "unique clock issuance IDs", clock)
    require(all(b["issue_time"] > a["issue_time"] for a, b in zip(rows, rows[1:])), "increasing issues", clock)
    for row in rows:
        issue, history = row["issue_time"], row["gap_history"]
        require(finite(issue) and issue < 2458119.5, "opened-period feature issue", clock)
        require(finite(row["available_at"]) and row["available_at"] <= issue, "feature availability", clock)
        require(row["prefix_last_jd"] is None or row["prefix_start"] < row["prefix_last_jd"] <= issue,
                "prefix support", clock)
        require(row["clock_anchor"] is None or finite(row["clock_anchor"]) and row["clock_anchor"] <= issue,
                "current anchor availability", clock)
        require(row["mark"] is None or finite(row["mark"]) and row["mark"] > 0, "positive mark or missing", clock)
        require(len({h["gap_id"] for h in history}) == len(history), "unique history IDs", clock)
        require(all(h["gap_id"] == h["left_candidate_id"] + ":" + h["right_candidate_id"] for h in history),
                "gap ID endpoint identity", clock)
        require(all(a["right_candidate_id"] == b["left_candidate_id"] for a, b in zip(history, history[1:])),
                "consecutive candidate slots without joins", clock)
        if row["previous_gap"] is not None:
            require(bool(history) and history[-1]["log_gap"] is not None
                    and close(row["previous_gap"], history[-1]["raw_gap"])
                    and close(math.log(row["previous_gap"]), history[-1]["log_gap"], 1e-12)
                    and row["previous_gap_covered"] is True, "previous-gap identity", clock)
        else:
            require(not history or history[-1]["log_gap"] is None, "previous-gap missing slot", clock)
        for h in history:
            require(finite(h["available_at"]) and h["available_at"] <= issue, "history availability", clock)
            if h["raw_gap"] is not None:
                require(finite(h["raw_gap"]) and h["raw_gap"] > 0, "positive raw history gap", clock)
            if h["log_gap"] is not None:
                require(finite(h["log_gap"]) and finite(h["raw_gap"])
                        and close(math.log(h["raw_gap"]), h["log_gap"], 1e-12), "log/raw history identity", clock)
                require(h["covered"] is True and h["longest_hole"] <= 7. and h["reason"] == "covered_adjacent_gap",
                        "measured history coverage", clock)
            if clock == "df" and h["anchor_emission_index"] is not None:
                source = audit[h["anchor_emission_index"]]
                require(source["status"] == "scheduled" and source["issue_time"] < issue,
                        "history anchor belongs to earlier scheduled issue")
                require(h["clock_anchor"] == source["anchor"] and h["anchor_available_at"] == source["anchor_available_at"],
                        "immutable history anchor and availability")
                require(h["anchor_available_at"] <= issue, "historical anchor available by current issue")
                scheduled_anchor_checks += 1
                historical_feature = df[source["emission_index"]]
                if historical_feature["clock_anchor"] is not None:
                    require(historical_feature["clock_anchor"] == h["clock_anchor"]
                            and historical_feature["anchor_available_at"] == h["anchor_available_at"],
                            "history matches earlier emitted clock")
                else:
                    source_fallbacks["all_history_slots"] += 1
                    if h["log_gap"] is not None:
                        source_fallbacks["measured_history_slots"] += 1
                if h["raw_gap"] is not None:
                    require(finite(h["onset_support"]) and h["onset_support"] <= issue
                            and close(h["raw_gap"], h["onset_support"] - h["clock_anchor"]),
                            "DF gap equals onset support minus immutable anchor")
            if clock == "df":
                for prefix in ("left_cadence_end", "right_cadence_on"):
                    value, available = h[prefix + "_days"], h[prefix + "_available_at"]
                    require(value is None or finite(value) and value >= 0 and finite(available) and available <= issue,
                            "historical cadence availability")
        for name in ("cadence_end", "cadence_on"):
            c = row[name]
            value = c["value_days"]
            if value is not None:
                require(finite(value) and value >= 0 and finite(c["available_at"]) and c["available_at"] <= issue,
                        "cadence feature availability", clock)
                require(row["prefix_start"] < c["lower_raw_at"] <= c["upper_raw_at"] <= issue
                        and close(value, c["upper_raw_at"] - c["lower_raw_at"]), "cadence raw support identity", clock)
        rate = row["observer_rate"]
        if rate["value_per_day"] is not None:
            require(finite(rate["available_at"]) and rate["available_at"] <= issue
                    and row["prefix_start"] < rate["span_start"] < rate["span_stop"] <= issue,
                    "rate support and availability", clock)
            require(rate["observer_nights"] > 0 and close(rate["value_per_day"], rate["observer_nights"] /
                    (rate["span_stop"] - rate["span_start"] + 1.))
                    and close(rate["log_value"], math.log(rate["value_per_day"]), 1e-12), "rate arithmetic", clock)
        proxy = row["flux_proxy"]
        require(finite(proxy["available_at"]) and proxy["available_at"] <= issue, "flux availability", clock)
        if proxy["support_start"] is not None:
            require(row["prefix_start"] < proxy["raw_visit_support_start"] <= proxy["support_start"]
                    <= proxy["support_stop"] <= proxy["raw_visit_support_stop"] <= issue,
                    "flux raw support", clock)
            require(proxy["span_start"] <= proxy["support_start"] <= proxy["support_stop"] <= proxy["span_stop"],
                    "flux no extrapolation", clock)
        if proxy["value_threshold_flux_days"] is not None:
            require(finite(proxy["value_threshold_flux_days"]) and proxy["value_threshold_flux_days"] >= 0
                    and proxy["status"] == "available" and proxy["balanced_night_points"] >= 2
                    and proxy["maximum_internal_gap_days"] <= 7., "flux availability semantics", clock)
        if clock == "df":
            own = audit[row["emission_index"]]
            require(own["status"] == "scheduled" and own["issue_time"] == issue
                    and row["anchor_available_at"] == own["anchor_available_at"], "DF own schedule identity")
            if row.get("historical_clock_anchor") is not None:
                require(row["clock_anchor"] == row["historical_clock_anchor"] == own["anchor"],
                        "zero current-own historical mismatch")
            require(row["flux_proxy"] == point[row["emission_index"]]["flux_proxy"]
                    and row["observer_rate"] == point[row["emission_index"]]["observer_rate"],
                    "matched-clock control identities")

coincident = [r for r in audit.values() if r["status"] == "coincident_pending_issue"]
for row in coincident:
    earlier = audit[row["coincident_with_emission_index"]]
    require(row["emission_index"] not in df and earlier["emission_index"] in df,
            "coincident later original retained only in audit")
    require(row["original_issue_time"] > earlier["original_issue_time"] and earlier["status"] == "scheduled"
            and all(row[k] == earlier[k] for k in ("issue_time", "anchor", "anchor_first_at", "anchor_available_at")),
            "coincident representative has exactly same scheduled clock")


def counts(rows):
    return {"issues": len(rows), "anchor": sum(r["clock_anchor"] is not None for r in rows),
            "mark": sum(r["mark"] is not None for r in rows),
            "gap": sum(r["previous_gap"] is not None for r in rows),
            "anchor_gap_mark": sum(all(r[k] is not None for k in ("clock_anchor", "previous_gap", "mark")) for r in rows),
            "statuses": dict(Counter(r["status"] for r in rows))}


periods = {}
for period, years in {"development": (1910, 1960), "evaluation": (1960, 2018)}.items():
    lo, hi = [date(y, 1, 1).toordinal() + 1721424.5 for y in years]
    selected = {clock: [r for r in ledgers[clock] if lo <= r["issue_time"] < hi]
                for clock in ("point_original", "df", "point_at_df")}
    left = {r["emission_index"]: r for r in selected["df"]}
    right = {r["emission_index"]: r for r in selected["point_at_df"]}
    markable = lambda row: all(row[k] is not None for k in ("clock_anchor", "previous_gap", "mark"))
    summary = {clock: counts(rows) for clock, rows in selected.items()}
    summary["joint_clocks_anchor_gap_mark"] = sum(markable(left[k]) and markable(right[k]) for k in left)
    summary["schedule_status_by_original_issue"] = dict(Counter(r["status"] for r in audit.values()
                                                               if lo <= r["original_issue_time"] < hi))
    summary["DF_median_delay_days"] = statistics.median(r["issue_delay_days"] for r in selected["df"])
    periods[period] = summary
    recorded = recorded_summary["periods"]["development_1910_1959" if period == "development" else "evaluation_1960_2017"]
    require(summary["joint_clocks_anchor_gap_mark"] == recorded["joint_clocks_anchor_gap_mark"], "independent paired markable count")
    for clock in selected:
        for key, recorded_key in (("issues", "features"), ("anchor", "anchor_available"), ("mark", "mark_available"),
                                  ("gap", "previous_gap_available"), ("anchor_gap_mark", "anchor_gap_mark_available"), ("statuses", "status")):
            require(summary[clock][key] == recorded[clock][recorded_key], "independent period counts", clock + ":" + key)

summary = {"scope": "independent saved-feature invariants only; no raw observations, model fits or scores",
           "status": "passed" if not errors else "failed", "assertions": sum(checks.values()),
           "checks": dict(sorted(checks.items())), "failures": errors, "input_sha256": inputs,
           "feature_counts": {clock: len(ledgers[clock]) for clock in ("point_original", "df", "point_at_df")},
           "historical_scheduled_anchor_checks": scheduled_anchor_checks,
           "historical_anchor_source_feature_fallbacks": dict(source_fallbacks),
           "coincident_audit_only_count": len(coincident), "periods": periods,
           "checker_sha256": sha(Path(__file__).read_bytes()),
           "limits": ["vector consistency does not rederive visits or causal scheduling from raw observations",
                      "historical onsets and gaps are current-prefix reconstructions, not immutable past measurements",
                      "cadence and rate fields are observation-conditioned sensitivities, not error bounds or pure negative controls"]}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n")
lines = ["# Independent R2b saved-feature audit", "", summary["scope"], "",
         f"Status: **{summary['status']}**; {summary['assertions']:,} assertions; {len(errors)} failures.",
         f"Verified all feature/source receipt hashes; {scheduled_anchor_checks:,} historical anchor links.",
         f"Coincident later originals retained only in the audit: {len(coincident)}.", "",
         f"Historical slots whose source emission had a fallback model clock: {source_fallbacks['all_history_slots']}; "
         f"{source_fallbacks['measured_history_slots']} of these slots contain measured gaps. Their anchors match the "
         "immutable scheduled observed anchors in the audit, not an earlier usable model clock. Later-prefix "
         "association can be resolved even when the earlier emission's predictor fell back.", "",
         "| Period | Original point | DF/matched point | DF markable | Jointly markable |",
         "|---|---:|---:|---:|---:|"]
for period, p in periods.items():
    lines.append(f"| {period} | {p['point_original']['issues']} | {p['df']['issues']} | {p['df']['anchor_gap_mark']} | {p['joint_clocks_anchor_gap_mark']} |")
lines += ["", "No numerical forecast, model or raw-observation code was imported. No fit outputs were read.",
          "Vector consistency does not independently rederive the raw visit construction or establish latent containment."]
if errors:
    lines += ["", "Failures:"] + ["- " + e for e in errors]
(OUT / "report.md").write_text("\n".join(lines) + "\n")
print(json.dumps({k: summary[k] for k in ("status", "assertions", "failures", "feature_counts", "periods")}, indent=2))
raise SystemExit(bool(errors))
