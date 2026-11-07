#!/usr/bin/env python3
"""Publish a small reviewed public decision package from an X3 summary.

This adapter deliberately reads the summary and receipt as data products.  It
does not publish raw metrics, observer metadata, heavy ledgers, or nested
record arrays.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any


ERAS = ("1910_1929", "1930_1949", "1950_1959")
DECISIVE_CASES = ("primary", "structured")
RULES = ("C1_7", "C2_095")
GATE_NAMES = (
    "onset_effective_coverage",
    "end_effective_coverage",
    "short_outside_mar_may_completeness",
    "false_confirmed_per_year",
    "operational_confirmation_unsafe_per_year",
    "total_bias",
    "operational_confirmation_premature_fraction",
    "operational_confirmation_missing_fraction",
    "state_cadence_no_match",
)
UNSAFE_NAME = "operational_confirmation_unsafe_per_year"
DIAGNOSTIC_NAMES = ("operational_confirmation_false_per_year",)
CONTEXT_METRICS = (
    "onset_effective_coverage", "end_effective_coverage",
    "onset_conditional_coverage", "end_conditional_coverage",
    "short_outside_mar_may_completeness", "false_confirmed_per_year",
    "operational_confirmation_unsafe_per_year", "oracle_r_all", "recovered_r",
    "total_bias", "selection_bias", "boundary_bias", "eligible_count",
    "onset_point_rmse", "end_point_rmse", "onset_mean_width", "end_mean_width",
    "batch_confirmation_premature_fraction", "operational_confirmation_premature_fraction",
    "operational_confirmation_missing_fraction", "operational_confirmation_lag_mean",
    "operational_confirmation_duplicate_emission_count",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _number(value: Any) -> float | None:
    if value in (None, "", "None", "null"):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _metric(metric: Any) -> dict[str, Any]:
    return metric if isinstance(metric, dict) else {}


def _find_source(path: Path, receipt_override: Path | None = None) -> tuple[Path, Path]:
    """Resolve a summary file/directory and its embedded run receipt."""
    if path.is_dir():
        summary_path = path / "fullsummary.json"
    else:
        summary_path = path
    if not summary_path.is_file():
        raise FileNotFoundError(f"fullsummary.json not found: {summary_path}")
    summary = json.loads(summary_path.read_text())
    receipt = summary.get("run_receipt")
    if not isinstance(receipt, dict):
        raise ValueError("fullsummary.json has no embedded run_receipt")
    receipt_path = receipt_override if receipt_override is not None else summary_path.parent / "receipt.json"
    if receipt_path.is_file():
        external = json.loads(receipt_path.read_text())
        if external.get("metrics_sha256") and receipt.get("metrics_sha256") \
                and external["metrics_sha256"] != receipt["metrics_sha256"]:
            raise ValueError("summary and external receipts disagree on metrics hash")
        receipt = external
    return summary_path, receipt_path if receipt_path.is_file() else summary_path


def _cell_index(summary: dict[str, Any]) -> dict[tuple[str, str, str, str, str, str], dict[str, Any]]:
    cells = summary.get("cells")
    if not isinstance(cells, list):
        raise ValueError("summary cells are missing")
    index = {}
    for cell in cells:
        if not isinstance(cell, dict):
            raise ValueError("summary contains a non-object cell")
        key = tuple(str(cell.get(name)) for name in
                    ("case", "stratum", "phase", "threshold", "extractor", "rule"))
        if any(value in ("None", "") for value in key):
            raise ValueError("summary contains a cell with an incomplete key")
        if key in index:
            raise ValueError(f"duplicate summary cell: {key}")
        index[key] = cell
    return index


def _decisive_cells(index: dict[tuple[str, str, str, str, str, str], dict[str, Any]], rule: str) -> list[dict[str, Any]]:
    cells = []
    for case in DECISIVE_CASES:
        for era in ERAS:
            for phase in ("random", "state"):
                key = (case, era, phase, "10.0", "X3", rule)
                if key not in index:
                    raise ValueError(f"missing decisive X3 cell: {key}")
                cells.append(index[key])
    return cells


def _required_metric(cell: dict[str, Any], name: str) -> dict[str, Any]:
    metrics = cell.get("metrics")
    metric = metrics.get(name) if isinstance(metrics, dict) else None
    if not isinstance(metric, dict):
        raise ValueError(f"cell is missing required metric: {name}")
    if any(key not in metric for key in ("estimate", "lower", "upper", "undefined")):
        raise ValueError(f"required metric has an incomplete interval: {name}")
    return metric


def _decision_row(cell: dict[str, Any]) -> dict[str, Any]:
    row = {name: cell.get(name, "") for name in
           ("case", "stratum", "phase", "threshold", "extractor", "rule")}
    errors = cell.get("extraction_errors", 0)
    row.update({"reviewed": "true", "verdict": cell.get("verdict", ""),
                "extraction_errors": errors,
                "extraction_error_verdict": "FAIL" if errors else "PASS"})
    criteria = cell.get("criteria", {})
    for name in GATE_NAMES:
        if name == "state_cadence_no_match" and cell.get("phase") != "state":
            metric = {}
        else:
            metric = _required_metric(cell, "cadence_no_match_fraction"
                                      if name == "state_cadence_no_match" else name)
            if name not in criteria:
                raise ValueError(f"cell is missing required gate verdict: {name}")
        row[f"{name}_estimate"] = metric.get("estimate", "")
        row[f"{name}_lower"] = metric.get("lower", "")
        row[f"{name}_upper"] = metric.get("upper", "")
        row[f"{name}_verdict"] = criteria.get(name, "")
    for name in DIAGNOSTIC_NAMES:
        metric = _required_metric(cell, name)
        for suffix in ("estimate", "mcse", "lower", "upper"):
            row[f"{name}_{suffix}"] = metric.get(suffix, "")
        row[f"{name}_diagnostic_only"] = "true"
    return row


def _decision_fields() -> list[str]:
    fields = ["case", "stratum", "phase", "threshold", "extractor", "rule", "reviewed", "verdict",
              "extraction_errors", "extraction_error_verdict"]
    for name in GATE_NAMES:
        fields.extend(f"{name}_{suffix}" for suffix in ("estimate", "lower", "upper", "verdict"))
    fields.extend(f"{name}_{suffix}" for name in DIAGNOSTIC_NAMES
                  for suffix in ("estimate", "mcse", "lower", "upper", "diagnostic_only"))
    return fields


def _range_summary(cells: list[dict[str, Any]], fields: tuple[str, ...]) -> dict[str, Any]:
    output = {}
    for field in fields:
        values = []
        for cell in cells:
            metric = _metric(cell.get("metrics", {}).get(field))
            value = _number(metric.get("estimate"))
            if value is not None:
                values.append(value)
        output[field] = {"minimum": min(values) if values else None,
                         "maximum": max(values) if values else None,
                         "defined_cells": len(values)}
    return output


def _public_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    """Whitelist receipt provenance; omit paths, runtime detail and arrays."""
    keys = (
        "status", "validation_base", "freeze_commit", "actual_commit",
        "completed_histories", "completed_metric_rows", "completion_count",
        "metrics_sha256", "metrics_hash",
        "ledger_sha256", "ledger_hash", "inputs_sha256", "cache_sha256", "parameters_sha256",
        "qualification_receipt_sha256", "calibration_receipt_sha256", "calibration_attempts_sha256",
        "candidate_commit", "candidate_file_sha256", "source_sha256", "runtime_source_sha256",
    )
    return {key: receipt[key] for key in keys if key in receipt}


def _validate_public_schema(summary: dict[str, Any], receipt: dict[str, Any]) -> None:
    required_receipt = ("status", "validation_base", "freeze_commit", "actual_commit",
                        "runtime_source_sha256", "completed_histories",
                        "completed_metric_rows", "completion_count", "task_manifest")
    missing = [key for key in required_receipt if key not in receipt]
    if missing:
        raise ValueError(f"receipt is missing required publication fields: {', '.join(missing)}")
    if not isinstance(receipt["runtime_source_sha256"], dict) or not receipt["runtime_source_sha256"]:
        raise ValueError("receipt runtime_source_sha256 must be a non-empty map")
    manifest = receipt["task_manifest"]
    if not isinstance(manifest, dict):
        raise ValueError("receipt task_manifest must be an object")
    for key in ("expected_histories", "expected_metric_rows", "expected_aggregate_cells"):
        if key not in manifest:
            raise ValueError(f"task_manifest is missing required count: {key}")
    if "selected" not in summary:
        raise ValueError("fullsummary is missing selected")
    decisions = summary.get("candidate_decisions")
    if not isinstance(decisions, list) or {item.get("rule") for item in decisions if isinstance(item, dict)} != set(RULES):
        raise ValueError("fullsummary candidate_decisions must contain both rules")


def publish(source: Path, output: Path, *, receipt: Path | None = None) -> dict[str, Any]:
    summary_path, receipt_path = _find_source(Path(source), receipt)
    summary = json.loads(summary_path.read_text())
    receipt = summary.get("run_receipt", {})
    if receipt_path != summary_path:
        external = json.loads(receipt_path.read_text())
        receipt = external
    if receipt.get("status") != "completed":
        raise ValueError("run receipt is not completed")
    _validate_public_schema(summary, receipt)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite output: {output}")
    index = _cell_index(summary)
    decision_rows = []
    decisions = []
    for rule in RULES:
        cells = _decisive_cells(index, rule)
        decisions.append({"rule": rule, "required_decisive_cells": 12,
                          "observed_decisive_cells": len(cells),
                          "verdict": next((item.get("verdict") for item in summary.get("candidate_decisions", [])
                                           if item.get("rule") == rule), "")})
        for cell in cells:
            decision_rows.append(_decision_row(cell))
    if len(decision_rows) != 24:
        raise AssertionError("public decision package must contain 24 decisive rows")

    contextual = [cell for cell in index.values() if cell.get("case") in {"v1", "offset", "alternative"}]
    manifest = {
        "scope": "reviewed public X3 validation decision; no raw arrays",
        "source_fullsummary_sha256": _sha256(summary_path),
        "source_receipt_sha256": _sha256(receipt_path) if receipt_path != summary_path else None,
        "run_counts": {key: receipt.get(key) for key in
                        ("completed_histories", "completed_metric_rows", "completion_count") if key in receipt},
        "task_manifest_counts": {key: receipt.get("task_manifest", {}).get(key)
                                  for key in ("expected_histories", "expected_metric_rows",
                                              "expected_aggregate_cells")
                                  if isinstance(receipt.get("task_manifest"), dict)
                                  and key in receipt["task_manifest"]},
        "provenance": _public_receipt(receipt),
        "candidate_decisions": decisions,
        "selected": summary["selected"],
        "diagnostic_ranges_at_magnitude_10": {
            case: {extractor: _range_summary(
                [cell for cell in contextual if cell.get("case") == case
                 and cell.get("extractor") == extractor and cell.get("threshold") == "10.0"],
                ("recovered_r", "oracle_r_all", "total_bias",
                 "onset_effective_coverage", "end_effective_coverage"))
                   for extractor in ("X1", "X2", "X3")}
            for case in ("v1", "offset", "alternative")},
        "decision_rows": 24,
    }
    output.mkdir(parents=False, exist_ok=False)
    decision_path = output / "public_decision.csv"
    with decision_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_decision_fields(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(decision_rows)
    manifest["public_decision_sha256"] = _sha256(decision_path)
    context_path = output / "public_diagnostics.csv"
    context_fields = ["case", "stratum", "phase", "threshold", "extractor", "rule",
                      "replicates", "verdict", "extraction_errors"]
    context_fields += [f"{name}_{suffix}" for name in CONTEXT_METRICS
                       for suffix in ("estimate", "lower", "upper", "undefined")]
    with context_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=context_fields, lineterminator="\n")
        writer.writeheader()
        for cell in index.values():
            row = {key: cell.get(key, "") for key in context_fields[:9]}
            for name in CONTEXT_METRICS:
                metric = _metric(cell.get("metrics", {}).get(name))
                row.update({f"{name}_{suffix}": metric.get(suffix, "")
                            for suffix in ("estimate", "lower", "upper", "undefined")})
            writer.writerow(row)
    manifest["public_diagnostics_sha256"] = _sha256(context_path)
    manifest["publisher_source_sha256"] = _sha256(Path(__file__))
    (output / "public_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="fullsummary.json or its containing directory")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path,
                        help="optional completed run receipt.json when it is outside the summary directory")
    args = parser.parse_args()
    publish(args.source, args.output, receipt=args.receipt)


if __name__ == "__main__":
    main()
