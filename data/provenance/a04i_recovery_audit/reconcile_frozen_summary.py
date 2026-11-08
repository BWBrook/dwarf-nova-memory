#!/usr/bin/env python3

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import sys


ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
AUDIT = ROOT / "outputs/a04i_recovery_independent_audit"
RUN = ROOT / "outputs/a04i_recovery_20261108"
SUMMARY = ROOT / "outputs/a04i_recovery_summary_20261108"
RULES = ("C1_7", "C2_095")
CASES = ("primary", "structured", "gross")
ERAS = ("1910_1929", "1930_1949", "1950_1959")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def number(value: str) -> float:
    return float(value) if value not in ("", None) else math.nan


def close(left: float, right: float, tolerance: float = 5e-12) -> bool:
    return math.isfinite(left) and math.isfinite(right) and abs(left - right) <= tolerance


with (AUDIT / "independent_cell_metrics.csv").open(newline="") as handle:
    independent = list(csv.DictReader(handle))
with (AUDIT / "independent_global_decisions.csv").open(newline="") as handle:
    independent_decisions = list(csv.DictReader(handle))
with (SUMMARY / "reviewed_summary.csv").open(newline="") as handle:
    reviewed_all = list(csv.DictReader(handle))
full = json.loads((SUMMARY / "fullsummary.json").read_text())
receipt = json.loads((RUN / "receipt.json").read_text())

reviewed = [
    row for row in reviewed_all
    if row["family"] == "v2-phase" and row["phase"] == "phase"
    and row["case"] in CASES and row["stratum"] in ERAS
    and float(row["threshold"]) == 10.0 and row["extractor"] == "X4"
    and row["rule"] in RULES
]
reviewed_map = {
    (row["family"], row["phase"], row["case"], row["stratum"], row["rule"]): row
    for row in reviewed
}

comparisons = []
maximum_difference = 0.0
for item in independent:
    key = tuple(item[name] for name in ("family", "phase", "case", "stratum", "rule"))
    summary_row = reviewed_map[key]
    metric = item["metric"]
    criteria = json.loads(summary_row["criteria_json"])
    numeric_matches = {}
    differences = {}
    for field in ("estimate", "lower", "upper"):
        independent_value = number(item[field])
        summary_value = number(summary_row[f"{metric}_{field}"])
        differences[field] = abs(independent_value - summary_value)
        maximum_difference = max(maximum_difference, differences[field])
        numeric_matches[field] = close(independent_value, summary_value)
    comparison = {
        "key": key,
        "metric": metric,
        "numeric_matches": numeric_matches,
        "differences": differences,
        "criterion_match": criteria.get(metric) == item["status"],
        "cell_verdict_match": summary_row["verdict"] == item["cell_verdict"],
        "replicates_match": int(summary_row["replicates"]) == int(item["replicates"]),
        "errors_match": int(summary_row["extraction_errors"]) == int(item["extraction_errors"]),
        "selected_rule_match": summary_row["selected_rule"] == "C1_7",
    }
    comparison["match"] = (
        all(numeric_matches.values()) and comparison["criterion_match"]
        and comparison["cell_verdict_match"] and comparison["replicates_match"]
        and comparison["errors_match"] and comparison["selected_rule_match"]
    )
    comparisons.append(comparison)


def margin(item: dict[str, str]) -> float:
    lower = float(item["lower"])
    upper = float(item["upper"])
    bound = float(item["bound"])
    if item["direction"] == "above":
        return lower - bound
    if item["direction"] == "below":
        return bound - upper
    if item["direction"] == "inside":
        return min(lower + bound, bound - upper)
    raise ValueError(item["direction"])


pass_metrics = [item for item in independent if item["status"] == "PASS"]
for item in pass_metrics:
    item["pass_margin"] = margin(item)
selected_pivotal = min(
    (item for item in pass_metrics if item["rule"] == "C1_7"),
    key=lambda item: item["pass_margin"],
)
overall_pivotal = min(pass_metrics, key=lambda item: item["pass_margin"])

decision_map = {item["rule"]: item for item in independent_decisions}
family_decisions = {
    item["rule"]: item for item in full["candidate_decisions"] if "family" in item
}
global_decisions = {
    item["rule"]: item for item in full["candidate_decisions"] if item.get("scope") == "global"
}
decision_matches = {}
for rule in RULES:
    independent_item = decision_map[rule]
    family_item = family_decisions[rule]
    global_item = global_decisions[rule]
    decision_matches[rule] = (
        independent_item["verdict"] == family_item["verdict"] == global_item["verdict"]
        and int(independent_item["ordinary_cells"]) == family_item["observed_ordinary_cells"] == 6
        and int(independent_item["gross_cells"]) == family_item["observed_gross_cells"] == 3
        and int(independent_item["pass_cells"]) == 9
        and family_item["cell_verdicts"] == ["PASS"] * 9
    )

summary_contract = {
    "reviewed_rows": len(reviewed_all) == 144,
    "decisive_rows": len(reviewed) == 18,
    "full_cells": len(full["cells"]) == 144,
    "input_metrics_hash": full["input_metrics_sha256"] == receipt["metrics_sha256"],
    "summarizer_source_hash": (
        full["summarizer_source_sha256"]
        == receipt["runtime_source_sha256"]["scripts/summarize_joint_recovery.py"]
    ),
    "grid_rows": full["expected_grid_rows"] == 16650,
    "ledger_records": full["expected_ledger_records"] == 9600,
    "selected": full["selected"] == {"extractor": "X4", "rule": "C1_7"},
}

reconciliation_pass = (
    len(comparisons) == 108
    and all(item["match"] for item in comparisons)
    and all(decision_matches.values())
    and all(summary_contract.values())
)


def pivotal_payload(item: dict[str, str]) -> dict[str, object]:
    return {
        "rule": item["rule"], "case": item["case"], "stratum": item["stratum"],
        "metric": item["metric"], "estimate": float(item["estimate"]),
        "lower": float(item["lower"]), "upper": float(item["upper"]),
        "bound": float(item["bound"]), "pass_margin": float(item["pass_margin"]),
    }


result = {
    "independent_derivation_preceded_summary_read": True,
    "independent_metric_comparisons": len(comparisons),
    "maximum_absolute_numeric_difference": maximum_difference,
    "all_cell_metrics_and_verdicts_match": all(item["match"] for item in comparisons),
    "decision_matches": decision_matches,
    "summary_contract": summary_contract,
    "selected_rule_pivotal_interval": pivotal_payload(selected_pivotal),
    "all_rules_pivotal_interval": pivotal_payload(overall_pivotal),
    "fullsummary_sha256": sha256(SUMMARY / "fullsummary.json"),
    "reviewed_summary_sha256": sha256(SUMMARY / "reviewed_summary.csv"),
    "reconciliation_pass": reconciliation_pass,
}
(AUDIT / "summary_reconciliation.json").write_text(
    json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
)

print("A04i independent-to-frozen-summary reconciliation")
print(f"independent_metric_comparisons={len(comparisons)}")
print(f"maximum_absolute_numeric_difference={maximum_difference:.17g}")
print(f"all_cell_metrics_and_verdicts_match={result['all_cell_metrics_and_verdicts_match']}")
for rule in RULES:
    print(f"decision_match_{rule}={decision_matches[rule]}")
print(f"frozen_selected={full['selected']}")
print("selected_rule_pivotal=" + json.dumps(result["selected_rule_pivotal_interval"], sort_keys=True))
print("all_rules_pivotal=" + json.dumps(result["all_rules_pivotal_interval"], sort_keys=True))
print(f"reconciliation_pass={reconciliation_pass}")
if not reconciliation_pass:
    raise SystemExit(1)
