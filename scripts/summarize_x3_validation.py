#!/usr/bin/env python3
"""Summarize and gate a completed A04e X3 validation run.

The input is an immutable runner directory containing ``metrics.csv`` and its
``receipt.json``.  This script never changes the run directory and writes a
new summary directory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev
from typing import Any, Iterable


CASES = ("primary", "structured", "alternative", "offset", "v1", "early")
STRATA = ("1900_1909", "1910_1929", "1930_1949", "1950_1959")
ERAS = ("1910_1929", "1930_1949", "1950_1959")
PHASES = ("random", "state")
EXTRACTORS = ("X1", "X2", "X3")
RULES = ("C1_7", "C2_095")
THRESHOLDS = (9.5, 10.0, 10.5)
Z95 = 1.96

KEYS = ("case", "stratum", "phase", "threshold", "extractor", "rule")
TASK_KEYS = ("case", "stratum", "phase", "replicate")

# Count ratios pool all event/count denominators.  The remaining listed
# diagnostics are replicate means, preserving undefined replicate counts.
RATIO_FIELDS = {
    "onset_effective_coverage": ("onset_effective_covered", "reference_event_count"),
    "end_effective_coverage": ("end_effective_covered", "reference_event_count"),
    "onset_conditional_coverage": ("onset_effective_covered", "onset_finite_matched_count"),
    "end_conditional_coverage": ("end_effective_covered", "end_finite_matched_count"),
    "short_outside_mar_may_completeness": (
        "short_outside_mar_may_complete_count", "short_outside_mar_may_count"),
    "completeness": ("completeness_count", "reference_event_count"),
    "unique_completeness": ("unique_completeness_count", "reference_event_count"),
    "false_confirmed_per_year": ("false_confirmed_count", "exposure_years"),
    "hidden_passed_fraction": ("hidden_passed", "pairs_passed"),
    "rejected_true_fraction": ("rejected_trueconsecutive", "mapped_trueconsecutive"),
    "type_error": ("type_misclassified_count", "duration_finite_matched_count"),
    "batch_confirmation_missing_fraction": (
        "batch_confirmation_missing_count", "batch_confirmation_candidate_count"),
    "batch_confirmation_premature_fraction": (
        "batch_confirmation_premature_count", "batch_confirmation_observed_count"),
    "batch_confirmation_premature_fraction_conservative": (
        "batch_confirmation_premature_count", "batch_confirmation_candidate_count"),
    "operational_confirmation_missing_fraction": (
        "operational_confirmation_missing_count", "operational_confirmation_candidate_count"),
    "operational_confirmation_premature_fraction": (
        "operational_confirmation_premature_count", "operational_confirmation_observed_count"),
    "operational_confirmation_premature_fraction_conservative": (
        "operational_confirmation_premature_count", "operational_confirmation_candidate_count"),
    "operational_confirmation_all_truth_sensitivity": (
        "operational_confirmation_all_truth_observed_count", "operational_confirmation_all_truth_count"),
    "operational_confirmation_all_truth_missing_fraction": (
        "operational_confirmation_all_truth_missing_count", "operational_confirmation_all_truth_count"),
    "operational_confirmation_all_truth_premature_fraction": (
        "operational_confirmation_all_truth_premature_count",
        "operational_confirmation_all_truth_observed_count"),
    "operational_confirmation_false_per_year": (
        "operational_confirmation_false_emission_count", "exposure_years"),
}

MEAN_FIELDS = (
    "oracle_r_all", "recovered_r", "selected_oracle_r", "recovered_matched_r",
    "total_bias", "selection_bias", "boundary_bias", "onset_point_bias", "end_point_bias",
    "onset_point_rmse", "end_point_rmse", "onset_mean_width", "end_mean_width",
    "duration_point_bias", "duration_point_rmse", "coverage_diagnostic_mean",
    "eligible_count", "censored_count", "pair_count", "invalid_pair_count", "association_n",
    "selected_association_n", "oracle_all_n", "onset_fallback_rate", "end_fallback_rate",
    "batch_confirmation_lag_mean", "batch_confirmation_lag_median", "batch_confirmation_lag_rmse",
    "batch_confirmation_candidate_count", "batch_confirmation_observed_count",
    "batch_confirmation_missing_count", "batch_confirmation_premature_count",
    "operational_confirmation_lag_mean", "operational_confirmation_lag_median",
    "operational_confirmation_lag_rmse", "cadence_no_match_fraction",
    "operational_confirmation_candidate_count", "operational_confirmation_observed_count",
    "operational_confirmation_missing_count", "operational_confirmation_premature_count",
    "operational_confirmation_all_truth_count", "operational_confirmation_all_truth_observed_count",
    "operational_confirmation_all_truth_missing_count", "operational_confirmation_all_truth_premature_count",
    "operational_confirmation_false_emission_count", "operational_confirmation_ambiguous_emission_count",
    "operational_confirmation_duplicate_emission_count", "operational_confirmation_emission_count",
    "cadence_no_match_days", "cadence_borrowed_days", "split_truth_count", "split_excess_count",
    "merged_episode_count", "merged_excess_count", "unconfirmed_barrier_count",
    "confirmed_extracted_count", "duration_finite_matched_count",
)

for _prefix in ("onset", "end"):
    for _method in ("fit", "adjacency", "other"):
        MEAN_FIELDS += (
            f"{_prefix}_{_method}_reference_count",
            f"{_prefix}_{_method}_finite_count",
            f"{_prefix}_{_method}_covered",
            f"{_prefix}_{_method}_effective_coverage",
            f"{_prefix}_{_method}_conditional_coverage",
        )

NESTED_FIELDS = ("completeness_by_true_type", "completeness_by_gregorian_month")
RARE_RATE_NAMES = {
    "batch_confirmation_missing_fraction",
    "batch_confirmation_premature_fraction",
    "batch_confirmation_premature_fraction_conservative",
    "operational_confirmation_missing_fraction",
    "operational_confirmation_premature_fraction",
    "operational_confirmation_premature_fraction_conservative",
}


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


def _json_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    return _number(value)


def _seed_int(value: Any) -> int | None:
    """Parse a decimal seed without lossy float conversion."""
    if value in (None, ""):
        return None
    try:
        text = str(value).strip()
        if not text or any(character not in "0123456789-" for character in text):
            return None
        return int(text)
    except (TypeError, ValueError):
        return None


def seed_for(base: Any, *labels: Any) -> int:
    """Match the runner's deterministic seed stream without importing it."""
    payload = "|".join(map(str, (base,) + labels)).encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def expected_grid() -> set[tuple[str, str, str, str, str, str, int]]:
    """Return the exact expected row key grid, including replicate IDs."""
    return _expected_grid()


def _expected_grid() -> set[tuple[str, str, str, str, str, str, int]]:
    # The helper above intentionally keeps the construction readable; primary
    # threshold-10 rows for IDs 200--399 are added separately here.
    rows = set()
    def add(case, strata, phases, reps, thresholds, rep_start=0):
        for stratum in strata:
            for phase in phases:
                for rep in range(rep_start, rep_start + reps):
                    for threshold in thresholds:
                        for extractor in EXTRACTORS:
                            for rule in RULES:
                                rows.add((case, stratum, phase, str(threshold), extractor, rule, rep))
    add("primary", ERAS, PHASES, 200, THRESHOLDS, 0)
    add("primary", ERAS, PHASES, 200, (10.0,), 200)
    add("alternative", ERAS, PHASES, 200, THRESHOLDS)
    add("offset", ERAS, ("random",), 200, (10.0,))
    add("v1", ERAS, ("random",), 200, (10.0,))
    add("early", ("1900_1909",), PHASES, 200, THRESHOLDS)
    add("structured", ERAS, PHASES, 400, (10.0,))
    return rows


def _validate_receipt(receipt: dict[str, Any], metrics_path: Path) -> None:
    if receipt.get("status") != "completed":
        raise ValueError("run receipt is not completed")
    expected = {"expected_histories": 7600, "expected_metric_rows": 79200,
                "completed_histories": 7600, "completed_metric_rows": 79200,
                "completion_count": 7600}
    for key, value in expected.items():
        if receipt.get(key) != value:
            raise ValueError(f"receipt {key} is not {value}")
    manifest = receipt.get("task_manifest")
    if not isinstance(manifest, dict) or manifest.get("expected_histories") != 7600 \
            or manifest.get("expected_metric_rows") != 79200:
        raise ValueError("receipt task manifest does not describe the full grid")
    if tuple(manifest.get("cases", ())) != CASES or tuple(manifest.get("extractors", ())) != EXTRACTORS \
            or tuple(manifest.get("rules", ())) != RULES:
        raise ValueError("receipt task manifest cases, extractors or rules differ")
    attempts = receipt.get("calibration_attempts_sha256")
    if attempts is not None:
        if not isinstance(attempts, dict) or not attempts:
            raise ValueError("receipt calibration_attempts_sha256 must be a non-empty map")
        if any(not isinstance(key, str) or not isinstance(value, str)
               or len(value) != 64 or any(character not in "0123456789abcdefABCDEF" for character in value)
               for key, value in attempts.items()):
            raise ValueError("receipt calibration_attempts_sha256 contains an invalid digest")
    if receipt.get("metrics_sha256") and receipt.get("metrics_hash") \
            and receipt["metrics_sha256"] != receipt["metrics_hash"]:
        raise ValueError("receipt metrics hashes disagree")
    digest = receipt.get("metrics_sha256") or receipt.get("metrics_hash")
    if digest != _sha256(metrics_path):
        raise ValueError("metrics.csv does not match receipt metrics_sha256")


def _normal_interval(estimate: float | None, mcse: float | None) -> tuple[float | None, float | None]:
    if estimate is None or mcse is None:
        return None, None
    return estimate - Z95 * mcse, estimate + Z95 * mcse


def ratio_interval(rows: list[dict[str, Any]], numerator: str, denominator: str,
                   *, rare: bool = False) -> dict[str, Any]:
    """Ratio of pooled counts with replicate-cluster delta MCSE."""
    pairs = [(_number(row.get(numerator)), _number(row.get(denominator))) for row in rows]
    if any(a is None or b is None or b < 0 for a, b in pairs):
        return {"estimate": None, "mcse": None, "lower": None, "upper": None,
                "undefined": len(rows)}
    total_denominator = sum(b for _, b in pairs)
    if total_denominator <= 0:
        return {"estimate": None, "mcse": None, "lower": None, "upper": None,
                "undefined": len(rows)}
    estimate = sum(a for a, _ in pairs) / total_denominator
    residuals = [a - estimate * b for a, b in pairs]
    mcse = (stdev(residuals) / math.sqrt(len(rows)) /
            (total_denominator / len(rows)) if len(rows) > 1 else None)
    lower, upper = _normal_interval(estimate, mcse)
    result = {"estimate": estimate, "mcse": mcse, "lower": lower, "upper": upper,
              "undefined": 0}
    if rare:
        result.update(_union_rare_interval(estimate, mcse, total_denominator,
                                           sum(a for a, _ in pairs), len(rows), lower, upper))
    return result


def _wilson(estimate: float, n_eff: float) -> tuple[float, float]:
    n_eff = max(1.0, float(n_eff))
    z2 = Z95 * Z95
    centre = (estimate + z2 / (2 * n_eff)) / (1 + z2 / n_eff)
    half = Z95 * math.sqrt(estimate * (1 - estimate) / n_eff + z2 / (4 * n_eff * n_eff)) \
        / (1 + z2 / n_eff)
    return centre - half, centre + half


def _union_rare_interval(estimate: float, mcse: float | None, denominator: float,
                         numerator: float, replicate_count: int,
                         lower: float | None, upper: float | None) -> dict[str, float]:
    if estimate <= 0.0 or estimate >= 1.0:
        n_eff = float(replicate_count)
    elif mcse is None or mcse == 0.0:
        n_eff = denominator
    else:
        n_eff = min(denominator, max(1.0, estimate * (1 - estimate) / (mcse * mcse)))
    wilson_lower, wilson_upper = _wilson(estimate, n_eff)
    return {"normal_lower": lower, "normal_upper": upper,
            "wilson_lower": wilson_lower, "wilson_upper": wilson_upper,
            "effective_n": n_eff,
            "lower": max(0.0, min(lower if lower is not None else 1.0, wilson_lower)),
            "upper": min(1.0, max(upper if upper is not None else 0.0, wilson_upper))}


def mean_interval(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    values = [_number(row.get(field)) for row in rows]
    finite = [value for value in values if value is not None]
    if not finite:
        return {"estimate": None, "mcse": None, "lower": None, "upper": None,
                "undefined": len(rows)}
    estimate = mean(finite)
    mcse = stdev(finite) / math.sqrt(len(finite)) if len(finite) > 1 else None
    lower, upper = _normal_interval(estimate, mcse)
    return {"estimate": estimate, "mcse": mcse, "lower": lower, "upper": upper,
            "undefined": len(rows) - len(finite)}


def _gate(metric: dict[str, Any], bound: float, direction: str) -> str:
    if metric.get("undefined", 0) or metric.get("lower") is None or metric.get("upper") is None:
        return "INCONCLUSIVE"
    lower, upper = metric["lower"], metric["upper"]
    if direction == "above":
        return "PASS" if lower >= bound else "FAIL" if upper < bound else "INCONCLUSIVE"
    if direction == "below":
        return "PASS" if upper < bound else "FAIL" if lower >= bound else "INCONCLUSIVE"
    if direction == "inside":
        return "PASS" if lower > -bound and upper < bound else \
            "FAIL" if lower >= bound or upper <= -bound else "INCONCLUSIVE"
    raise ValueError(f"unknown gate direction {direction}")


def _parse_nested(rows: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    totals: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in rows:
        raw = row.get(field)
        if raw in (None, "", "None", "null"):
            continue
        try:
            payload = json.loads(raw) if isinstance(raw, str) else raw
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        for key, values in payload.items():
            if not isinstance(values, dict):
                continue
            for count in ("reference_count", "complete_count", "unique_complete_count"):
                number = _number(values.get(count))
                if number is not None:
                    totals[str(key)][count] += int(number)
    result = {}
    for key, values in sorted(totals.items()):
        reference = values.get("reference_count", 0)
        complete = values.get("complete_count", 0)
        unique = values.get("unique_complete_count", 0)
        result[key] = {"reference_count": reference, "complete_count": complete,
                       "unique_complete_count": unique,
                       "completeness": complete / reference if reference else None,
                       "unique_completeness": unique / reference if reference else None}
    return result


def _validate_rows(rows: list[dict[str, Any]], receipt: dict[str, Any]) -> None:
    expected = _expected_grid()
    seen: set[tuple[str, str, str, str, str, str, int]] = set()
    tasks: dict[tuple[str, str, str, int], tuple[Any, Any, Any]] = {}
    for row_number, row in enumerate(rows, start=2):
        if any(not row.get(key) for key in KEYS):
            raise ValueError(f"metrics row {row_number} has an incomplete key")
        threshold = _number(row["threshold"])
        if threshold is None or threshold not in THRESHOLDS:
            raise ValueError(f"metrics row {row_number} has an invalid threshold")
        replicate = _number(row.get("replicate"))
        if replicate is None or int(replicate) != replicate or replicate < 0:
            raise ValueError(f"metrics row {row_number} has an invalid replicate")
        key = (row["case"], row["stratum"], row["phase"], str(threshold),
               row["extractor"], row["rule"], int(replicate))
        if key in seen:
            raise ValueError(f"duplicate metrics cell at row {row_number}")
        seen.add(key)
        task_key = (row["case"], row["stratum"], row["phase"], int(replicate))
        seeds = (row.get("seed"), row.get("truth_seed"), row.get("measurement_seed"))
        seed_numbers = tuple(_seed_int(value) for value in seeds)
        if any(value is None for value in seed_numbers):
            raise ValueError(f"metrics row {row_number} has missing seed metadata")
        previous = tasks.setdefault(task_key, seed_numbers)
        if previous != seed_numbers:
            raise ValueError(f"inconsistent seed metadata for {task_key}")
        base = receipt.get("validation_base")
        if base:
            expected_seed = seed_for(base, row["case"], row["stratum"], row["phase"], int(replicate))
            expected_truth = seed_for(expected_seed, "truth")
            expected_measurement = seed_for(expected_seed, "measurement")
            if seed_numbers != (expected_seed, expected_truth, expected_measurement):
                raise ValueError(f"seed stream mismatch for {task_key}")
    if seen != expected:
        missing = len(expected - seen)
        extra = len(seen - expected)
        raise ValueError(f"metrics grid mismatch: {missing} missing, {extra} unspecified rows")


def _cell_summary(key: tuple[str, str, str, str, str, str], rows: list[dict[str, Any]]) -> dict[str, Any]:
    metrics: dict[str, dict[str, Any]] = {}
    for name, (numerator, denominator) in RATIO_FIELDS.items():
        metrics[name] = ratio_interval(rows, numerator, denominator, rare=name in RARE_RATE_NAMES)
    for field in MEAN_FIELDS:
        metrics[field] = mean_interval(rows, field)

    criteria = {
        "onset_effective_coverage": _gate(metrics["onset_effective_coverage"], .90, "above"),
        "end_effective_coverage": _gate(metrics["end_effective_coverage"], .90, "above"),
        "short_outside_mar_may_completeness": _gate(metrics["short_outside_mar_may_completeness"], .95, "above"),
        "false_confirmed_per_year": _gate(metrics["false_confirmed_per_year"], .20, "below"),
        "operational_confirmation_false_per_year": _gate(
            metrics["operational_confirmation_false_per_year"], .20, "below"),
        "total_bias": _gate(metrics["total_bias"], .02, "inside"),
        "operational_confirmation_premature_fraction": _gate(
            metrics["operational_confirmation_premature_fraction"], .02, "below"),
        "operational_confirmation_missing_fraction": _gate(
            metrics["operational_confirmation_missing_fraction"], .05, "below"),
    }
    if key[0] in ("primary", "structured") and key[2] == "state":
        no_match = metrics["cadence_no_match_fraction"]
        if no_match["estimate"] is None or no_match["estimate"] > .10:
            criteria["state_cadence_no_match"] = "INCONCLUSIVE"
        else:
            criteria["state_cadence_no_match"] = "PASS"
    errors = sum(str(row.get("extraction_error", "")).strip().casefold()
                 not in {"", "0", "false", "none", "null"} for row in rows)
    if errors:
        verdict = "FAIL"
    elif any(value == "FAIL" for value in criteria.values()):
        verdict = "FAIL"
    elif all(value == "PASS" for value in criteria.values()):
        verdict = "PASS"
    else:
        verdict = "INCONCLUSIVE"
    nested = {field: _parse_nested(rows, field) for field in NESTED_FIELDS}
    return {**dict(zip(KEYS, key)), "replicates": len(rows), "extraction_errors": errors,
            "verdict": verdict, "criteria": criteria, "metrics": metrics,
            "nested_diagnostics": nested}


def candidate_decisions(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Evaluate both rules against all twelve decisive X3 cells."""
    decisions = []
    for rule in RULES:
        selected_cells = [cell for cell in cells if cell["case"] in ("primary", "structured")
                          and cell["stratum"] in ERAS and cell["phase"] in PHASES
                          and cell["threshold"] == "10.0" and cell["extractor"] == "X3"
                          and cell["rule"] == rule]
        statuses = [cell["verdict"] for cell in selected_cells]
        decision = "PASS" if len(selected_cells) == 12 and statuses and all(status == "PASS" for status in statuses) \
            else "FAIL" if any(status == "FAIL" for status in statuses) else "INCONCLUSIVE"
        decisions.append({"extractor": "X3", "rule": rule,
                          "required_decisive_cells": 12,
                          "observed_decisive_cells": len(selected_cells),
                          "cell_verdicts": statuses, "verdict": decision})
    return decisions


def choose_rule(decisions: list[dict[str, Any]]) -> str | None:
    """Select C1 globally, then C2 globally; never switch rules by cell."""
    for rule in RULES:
        if next(item for item in decisions if item["rule"] == rule)["verdict"] == "PASS":
            return rule
    return None


def summarize(directory: Path, output: Path) -> dict[str, Any]:
    directory = Path(directory)
    output = Path(output)
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    receipt_path = directory / "receipt.json"
    metrics_path = directory / "metrics.csv"
    receipt = json.loads(receipt_path.read_text())
    _validate_receipt(receipt, metrics_path)
    with metrics_path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 79200:
        raise ValueError(f"metrics.csv has {len(rows)} rows, expected 79200")
    _validate_rows(rows, receipt)
    grouped: dict[tuple[str, str, str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        threshold = str(_number(row["threshold"]))
        grouped[(row["case"], row["stratum"], row["phase"], threshold,
                 row["extractor"], row["rule"])].append(row)
    cells = [_cell_summary(key, grouped[key]) for key in sorted(grouped)]

    decisions = candidate_decisions(cells)
    selected_rule = choose_rule(decisions)
    selected = {"extractor": "X3", "rule": selected_rule} if selected_rule else None
    summary = {
        "scope": "A04e independent X3 validation; synthetic histories only",
        "run_receipt": receipt,
        "input_metrics_sha256": _sha256(metrics_path),
        "summarizer_source_sha256": _sha256(Path(__file__)),
        "cells": cells,
        "candidate_decisions": decisions,
        "selected": selected,
        "contextual_summaries": [cell for cell in cells if cell["case"] not in ("primary", "structured") or cell["threshold"] != "10.0"],
        "decisive_summaries": [cell for cell in cells if cell["case"] in ("primary", "structured") and cell["threshold"] == "10.0"],
    }
    sidecar = directory / "x3_threshold10_ledger.jsonl.gz"
    if sidecar.exists():
        summary["heavy_sidecar"] = {"path": sidecar.name, "sha256": _sha256(sidecar)}
    output.mkdir(parents=False, exist_ok=False)
    (output / "fullsummary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n")
    public_fields = ["case", "stratum", "phase", "threshold", "extractor", "rule", "replicates",
                     "verdict", "selected_rule", "onset_effective_coverage", "end_effective_coverage",
                     "short_outside_mar_may_completeness", "false_confirmed_per_year",
                     "operational_confirmation_false_per_year", "total_bias",
                     "operational_confirmation_premature_fraction",
                     "operational_confirmation_missing_fraction"]
    with (output / "smallpublicsummary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=public_fields, lineterminator="\n")
        writer.writeheader()
        for cell in cells:
            if cell["case"] not in ("primary", "structured") or cell["extractor"] != "X3":
                continue
            row = {field: cell.get(field, "") for field in public_fields[:9]}
            row["selected_rule"] = selected_rule or ""
            for field in public_fields[9:]:
                metric = cell["metrics"][field]
                row[field] = metric["estimate"]
            writer.writerow(row)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summarize(args.run_directory, args.output)


if __name__ == "__main__":
    main()
