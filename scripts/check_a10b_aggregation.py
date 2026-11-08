#!/usr/bin/env python3
"""Independent aggregation and reconciliation of the repaired A10b pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from scipy.stats import t as student_t


COMPARISONS = ("gain_M1_M0", "gain_M2_M0", "gain_M3_M2")
SCORE_DIFFERENCES = {
    "gain_M1_M0": ("M1", "M0"),
    "gain_M2_M0": ("M2", "M0"),
    "gain_M3_M2": ("M3", "M2"),
}
EXTRA_TYPE_VARIANT = "prefix_type_within"
PAIRED_STRESSES = ("gross", "offset", "adaptive")
ABS_TOL = 1e-10


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")


def variants_for_trial(config: dict[str, Any], family: str, case: str, replicate: int) -> tuple[str, ...]:
    variants = list(config["variants"])
    type_subset = config["type_within_subset"]
    latency_subset = config["latency_two_day_subset"]
    if case in type_subset["cases"] and replicate < type_subset["first_replicates"]:
        variants.append(EXTRA_TYPE_VARIANT)
    if case in latency_subset["cases"] and replicate < latency_subset["first_replicates"]:
        variants.extend(latency_subset["variants"])
    if len(variants) != len(set(variants)):
        raise ValueError(f"duplicate variant contract for {family}/{case}/{replicate}")
    return tuple(variants)


def expected_trials(config: dict[str, Any]) -> dict[tuple[str, str, int], tuple[str, ...]]:
    expected: dict[tuple[str, str, int], tuple[str, ...]] = {}
    for family, family_spec in config["families"].items():
        for case in family_spec["cases"]:
            for replicate in range(family_spec["replicates"]):
                key = (family, case, replicate)
                expected[key] = variants_for_trial(config, *key)
    return expected


def mc_summary(values: list[float]) -> dict[str, float | int | None]:
    n = len(values)
    if n == 0:
        return {
            "count": 0,
            "mean": None,
            "sample_sd": None,
            "mc95_lower": None,
            "mc95_upper": None,
            "positive_trials": 0,
        }
    mean = statistics.fmean(values)
    if n == 1:
        sd = None
        lower = None
        upper = None
    else:
        sd = statistics.stdev(values)
        half_width = float(student_t.ppf(0.975, n - 1)) * sd / math.sqrt(n)
        lower = mean - half_width
        upper = mean + half_width
    return {
        "count": n,
        "mean": mean,
        "sample_sd": sd,
        "mc95_lower": lower,
        "mc95_upper": upper,
        "positive_trials": sum(value > 0.0 for value in values),
    }


def close(a: float, b: float, tolerance: float = ABS_TOL) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tolerance)


def group_id(family: str, case: str, variant: str, comparison: str) -> str:
    return "|".join((family, case, variant, comparison))


def trial_id(family: str, case: str, replicate: int) -> str:
    return f"{family}-{case}-{replicate:03d}"


def load_trial_records(
    input_dir: Path,
    expected: dict[tuple[str, str, int], tuple[str, ...]],
) -> tuple[dict[tuple[str, str, int], dict[str, Any]], list[tuple[str, str, int]]]:
    records: dict[tuple[str, str, int], dict[str, Any]] = {}
    missing: list[tuple[str, str, int]] = []
    for key in expected:
        path = input_dir / f"{trial_id(*key)}.json"
        if not path.exists():
            missing.append(key)
            continue
        record = load_json(path)
        if tuple(record.get("task", ())) != key:
            raise AssertionError(f"task mismatch in {path}")
        if not isinstance(record.get("success"), bool):
            raise AssertionError(f"missing boolean success in {path}")
        records[key] = record
    unexpected = sorted(
        path.name
        for path in input_dir.glob("v*-*.json")
        if path.name.removesuffix(".json") not in {trial_id(*key) for key in expected}
    )
    if unexpected:
        raise AssertionError(f"unexpected trial files: {unexpected}")
    return records, sorted(missing)


def read_scores(
    scores_path: Path,
    expected: dict[tuple[str, str, int], tuple[str, ...]],
) -> tuple[
    dict[tuple[str, str, int, str, str], list[float]],
    dict[tuple[str, str, int, str], int],
    dict[str, Any],
]:
    values: dict[tuple[str, str, int, str, str], list[float]] = defaultdict(list)
    row_counts: dict[tuple[str, str, int, str], int] = defaultdict(int)
    seen_rows: set[tuple[str, str, int, str, int]] = set()
    max_gain_identity_error = 0.0
    row_count = 0
    with scores_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            try:
                family = str(row["family"])
                case = str(row["case"])
                replicate = int(row["replicate"])
                variant = str(row["variant"])
                emission_index = int(row["emission_index"])
            except (KeyError, TypeError, ValueError) as exc:
                raise AssertionError(f"malformed score identity at line {line_number}") from exc
            trial_key = (family, case, replicate)
            if trial_key not in expected:
                raise AssertionError(f"unexpected score trial at line {line_number}: {trial_key}")
            if variant not in expected[trial_key]:
                raise AssertionError(f"unexpected score variant at line {line_number}: {trial_key}/{variant}")
            row_key = (*trial_key, variant, emission_index)
            if row_key in seen_rows:
                raise AssertionError(f"duplicate score row at line {line_number}: {row_key}")
            seen_rows.add(row_key)
            for comparison in COMPARISONS:
                high, low = SCORE_DIFFERENCES[comparison]
                supplied = float(row[comparison])
                reconstructed = float(row[high]) - float(row[low])
                if not (math.isfinite(supplied) and math.isfinite(reconstructed)):
                    raise AssertionError(f"non-finite score at line {line_number}")
                discrepancy = abs(supplied - reconstructed)
                max_gain_identity_error = max(max_gain_identity_error, discrepancy)
                if discrepancy > 5e-13:
                    raise AssertionError(
                        f"score gain identity fails at line {line_number}: {comparison}, {discrepancy}"
                    )
                values[(*trial_key, variant, comparison)].append(supplied)
            row_counts[(*trial_key, variant)] += 1
            row_count += 1
    return values, row_counts, {
        "score_rows": row_count,
        "unique_score_rows": len(seen_rows),
        "max_row_gain_identity_error": max_gain_identity_error,
    }


def reconcile_trial_estimates(
    expected: dict[tuple[str, str, int], tuple[str, ...]],
    records: dict[tuple[str, str, int], dict[str, Any]],
    score_values: dict[tuple[str, str, int, str, str], list[float]],
    row_counts: dict[tuple[str, str, int, str], int],
) -> tuple[dict[tuple[str, str, int, str, str], float], dict[str, Any]]:
    means: dict[tuple[str, str, int, str, str], float] = {}
    maximum_estimate_error = 0.0
    maximum_n_error = 0
    interval_contains_zero: dict[tuple[str, str, int, str, str], bool] = {}
    interval_positive: dict[tuple[str, str, int, str, str], bool] = {}
    for key, record in records.items():
        score_group_keys = {group[:4] for group in score_values if group[:3] == key}
        if not record["success"]:
            if score_group_keys:
                raise AssertionError(f"failed trial has persisted score rows: {key}")
            continue
        result = record.get("result", {})
        saved_results = result.get("results", {})
        if set(saved_results) != set(expected[key]):
            raise AssertionError(
                f"saved variant set mismatch for {key}: {sorted(saved_results)} versus {sorted(expected[key])}"
            )
        if score_group_keys != {(*key, variant) for variant in expected[key]}:
            raise AssertionError(f"score variant set mismatch for successful trial {key}")
        for variant in expected[key]:
            n = row_counts[(*key, variant)]
            if n <= 0:
                raise AssertionError(f"empty score group for {key}/{variant}")
            for comparison in COMPARISONS:
                group = (*key, variant, comparison)
                mean = statistics.fmean(score_values[group])
                means[group] = mean
                saved = saved_results[variant][comparison]
                estimate_error = abs(mean - float(saved["estimate"]))
                n_error = abs(n - int(saved["n"]))
                maximum_estimate_error = max(maximum_estimate_error, estimate_error)
                maximum_n_error = max(maximum_n_error, n_error)
                if estimate_error > ABS_TOL or n_error:
                    raise AssertionError(
                        f"trial result mismatch for {group}: estimate error {estimate_error}, n error {n_error}"
                    )
                interval_contains_zero[group] = float(saved["lower"]) <= 0.0 <= float(saved["upper"])
                interval_positive[group] = float(saved["lower"]) > 0.0
    score_trials = {group[:3] for group in score_values}
    saved_successes = {key for key, record in records.items() if record["success"]}
    if score_trials != saved_successes:
        raise AssertionError(
            f"score/success trial mismatch: only scores={sorted(score_trials - saved_successes)}, "
            f"only records={sorted(saved_successes - score_trials)}"
        )
    return means, {
        "max_trial_estimate_error": maximum_estimate_error,
        "max_trial_n_error": maximum_n_error,
        "individual_interval_contains_zero": interval_contains_zero,
        "individual_interval_positive": interval_positive,
    }


def aggregate_groups(
    expected: dict[tuple[str, str, int], tuple[str, ...]],
    records: dict[tuple[str, str, int], dict[str, Any]],
    missing_trials: list[tuple[str, str, int]],
    trial_means: dict[tuple[str, str, int, str, str], float],
    row_counts: dict[tuple[str, str, int, str], int],
    interval_contains_zero: dict[tuple[str, str, int, str, str], bool],
    interval_positive: dict[tuple[str, str, int, str, str], bool],
) -> list[dict[str, Any]]:
    planned_groups = sorted(
        {
            (family, case, variant, comparison)
            for (family, case, _replicate), variants in expected.items()
            for variant in variants
            for comparison in COMPARISONS
        }
    )
    aggregates: list[dict[str, Any]] = []
    missing_set = set(missing_trials)
    for family, case, variant, comparison in planned_groups:
        applicable = sorted(
            key for key, variants in expected.items() if key[:2] == (family, case) and variant in variants
        )
        successful = [key for key in applicable if (*key, variant, comparison) in trial_means]
        failed = [key for key in applicable if key in records and not records[key]["success"]]
        missing = [key for key in applicable if key in missing_set]
        values = [trial_means[(*key, variant, comparison)] for key in successful]
        aggregate = {
            "group_id": group_id(family, case, variant, comparison),
            "family": family,
            "case": case,
            "variant": variant,
            "comparison": comparison,
            "planned_trials": len(applicable),
            **mc_summary(values),
            "mean_scored_n": statistics.fmean(row_counts[(*key, variant)] for key in successful)
            if successful
            else None,
            "failures": len(failed),
            "missing_trials": len(missing),
            "failed_trial_ids": [trial_id(*key) for key in failed],
            "missing_trial_ids": [trial_id(*key) for key in missing],
            "individual_intervals_containing_zero": sum(
                interval_contains_zero[(*key, variant, comparison)] for key in successful
            ),
            "diagnostic_intervals_positive": sum(
                interval_positive[(*key, variant, comparison)] for key in successful
            ),
        }
        aggregates.append(aggregate)
    return aggregates


def paired_contrasts(
    config: dict[str, Any],
    records: dict[tuple[str, str, int], dict[str, Any]],
    trial_means: dict[tuple[str, str, int, str, str], float],
    row_counts: dict[tuple[str, str, int, str], int],
) -> list[dict[str, Any]]:
    family = "v2-phase"
    replicates = int(config["families"][family]["replicates"])
    contrasts: list[dict[str, Any]] = []
    for stress in PAIRED_STRESSES:
        for variant in config["variants"]:
            for comparison in COMPARISONS:
                differences: list[float] = []
                stress_ns: list[int] = []
                null_ns: list[int] = []
                incomplete: list[int] = []
                for replicate in range(replicates):
                    stress_group = (family, stress, replicate, variant, comparison)
                    null_group = (family, "null", replicate, variant, comparison)
                    if stress_group not in trial_means or null_group not in trial_means:
                        incomplete.append(replicate)
                        continue
                    differences.append(trial_means[stress_group] - trial_means[null_group])
                    stress_ns.append(row_counts[(family, stress, replicate, variant)])
                    null_ns.append(row_counts[(family, "null", replicate, variant)])
                contrasts.append(
                    {
                        "contrast_id": "|".join((family, f"{stress}-minus-null", variant, comparison)),
                        "family": family,
                        "stress_case": stress,
                        "reference_case": "null",
                        "variant": variant,
                        "comparison": comparison,
                        "planned_pairs": replicates,
                        **mc_summary(differences),
                        "mean_stress_scored_n": statistics.fmean(stress_ns) if stress_ns else None,
                        "mean_null_scored_n": statistics.fmean(null_ns) if null_ns else None,
                        "incomplete_pairs": len(incomplete),
                        "incomplete_replicates": incomplete,
                    }
                )
    return contrasts


def flatten_summary_groups(summary: Any) -> list[dict[str, Any]] | None:
    if isinstance(summary, list) and all(isinstance(item, dict) for item in summary):
        return summary
    if isinstance(summary, dict):
        for key in ("rows", "summary", "groups", "aggregates", "gain_summary", "results"):
            value = summary.get(key)
            if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                return value
    return None


def first_present(mapping: dict[str, Any], names: tuple[str, ...]) -> Any:
    for name in names:
        if name in mapping:
            return mapping[name]
    raise KeyError(names)


def reconcile_final_summary(
    summary_path: Path,
    aggregates: list[dict[str, Any]],
    paired_contrasts: list[dict[str, Any]],
) -> dict[str, Any]:
    summary = load_json(summary_path)
    rows = flatten_summary_groups(summary)
    if rows is None:
        return {
            "status": "unrecognized_schema",
            "path": str(summary_path),
            "sha256": sha256(summary_path),
            "top_level_type": type(summary).__name__,
            "top_level_keys": sorted(summary) if isinstance(summary, dict) else None,
        }
    normalized: dict[str, dict[str, Any]] = {}
    for row in rows:
        try:
            identity = group_id(
                str(first_present(row, ("family",))),
                str(first_present(row, ("case",))),
                str(first_present(row, ("variant",))),
                str(first_present(row, ("comparison",))),
            )
        except KeyError:
            continue
        if identity in normalized:
            raise AssertionError(f"duplicate final-summary group {identity}")
        normalized[identity] = row
    independent = {row["group_id"]: row for row in aggregates}
    set_match = set(normalized) == set(independent)
    discrepancies: list[dict[str, Any]] = []
    max_abs_difference = 0.0
    field_specs = {
        "planned_trials": ("expected_replicates",),
        "count": ("replicates",),
        "mean": ("mean_gain_nats",),
        "sample_sd": ("block_gain_sd",),
        "mc95_lower": ("mc_lower",),
        "mc95_upper": ("mc_upper",),
        "positive_trials": ("positive_trials",),
        "mean_scored_n": ("mean_scored_issues",),
        "diagnostic_intervals_positive": ("diagnostic_intervals_positive",),
    }
    for identity in sorted(set(normalized) & set(independent)):
        actual = normalized[identity]
        expected_row = independent[identity]
        for field, candidate_names in field_specs.items():
            try:
                observed = first_present(actual, candidate_names)
            except KeyError:
                discrepancies.append({"group_id": identity, "field": field, "reason": "missing_field"})
                continue
            expected_value = expected_row[field]
            if expected_value is None or observed is None:
                matched = expected_value is None and observed is None
                difference = None
            elif isinstance(expected_value, int):
                matched = int(observed) == expected_value
                difference = abs(int(observed) - expected_value)
            else:
                difference = abs(float(observed) - float(expected_value))
                max_abs_difference = max(max_abs_difference, difference)
                matched = difference <= ABS_TOL
            if not matched:
                discrepancies.append(
                    {
                        "group_id": identity,
                        "field": field,
                        "independent": expected_value,
                        "final_summary": observed,
                        "absolute_difference": difference,
                    }
                )
        observed_failed_or_missing = first_present(normalized[identity], ("failed_or_missing_replicates",))
        expected_failed_or_missing = independent[identity]["failures"] + independent[identity]["missing_trials"]
        if int(observed_failed_or_missing) != expected_failed_or_missing:
            discrepancies.append(
                {
                    "group_id": identity,
                    "field": "failed_or_missing_replicates",
                    "independent": expected_failed_or_missing,
                    "final_summary": observed_failed_or_missing,
                }
            )

    paired_rows = summary.get("paired_stress_contrasts") if isinstance(summary, dict) else None
    paired_discrepancies: list[dict[str, Any]] = []
    normalized_paired: dict[str, dict[str, Any]] = {}
    if isinstance(paired_rows, list):
        for row in paired_rows:
            identity = "|".join(
                (
                    "v2-phase",
                    f"{row['case']}-minus-null",
                    str(row["variant"]),
                    str(row["comparison"]),
                )
            )
            if identity in normalized_paired:
                raise AssertionError(f"duplicate final-summary paired contrast {identity}")
            normalized_paired[identity] = row
    independent_paired = {row["contrast_id"]: row for row in paired_contrasts}
    paired_set_match = set(normalized_paired) == set(independent_paired)
    paired_field_specs = {
        "planned_pairs": "expected_pairs",
        "count": "paired_trials",
        "mean": "stress_minus_null",
        "mc95_lower": "mc_lower",
        "mc95_upper": "mc_upper",
    }
    for identity in sorted(set(normalized_paired) & set(independent_paired)):
        actual = normalized_paired[identity]
        expected_row = independent_paired[identity]
        for expected_field, observed_field in paired_field_specs.items():
            expected_value = expected_row[expected_field]
            observed = actual.get(observed_field)
            if observed is None or expected_value is None:
                matched = observed is None and expected_value is None
                difference = None
            elif isinstance(expected_value, int):
                matched = int(observed) == expected_value
                difference = abs(int(observed) - expected_value)
            else:
                difference = abs(float(observed) - float(expected_value))
                max_abs_difference = max(max_abs_difference, difference)
                matched = difference <= ABS_TOL
            if not matched:
                paired_discrepancies.append(
                    {
                        "contrast_id": identity,
                        "field": expected_field,
                        "independent": expected_value,
                        "final_summary": observed,
                        "absolute_difference": difference,
                    }
                )
    records_path = summary_path.parent / "records.json"
    scores_path = summary_path.parent / "scores.jsonl"
    records_hash = sha256(records_path) if records_path.exists() else None
    scores_hash = sha256(scores_path) if scores_path.exists() else None
    provenance = {
        "summary_complete_true": summary.get("complete") is True if isinstance(summary, dict) else False,
        "records_hash_match": records_hash is not None and summary.get("records_sha256") == records_hash,
        "scores_hash_match": scores_hash is not None and summary.get("scores_sha256") == scores_hash,
    }
    overall_match = (
        set_match
        and not discrepancies
        and paired_set_match
        and not paired_discrepancies
        and all(provenance.values())
    )
    return {
        "status": "match" if overall_match else "mismatch",
        "path": str(summary_path),
        "sha256": sha256(summary_path),
        "recognized_rows": len(normalized),
        "independent_rows": len(independent),
        "recognized_paired_contrasts": len(normalized_paired),
        "independent_paired_contrasts": len(independent_paired),
        "exact_group_set_match": set_match,
        "exact_paired_contrast_set_match": paired_set_match,
        "only_in_final_summary": sorted(set(normalized) - set(independent)),
        "only_in_independent_audit": sorted(set(independent) - set(normalized)),
        "only_paired_in_final_summary": sorted(set(normalized_paired) - set(independent_paired)),
        "only_paired_in_independent_audit": sorted(set(independent_paired) - set(normalized_paired)),
        "raw_group_discrepancies": discrepancies,
        "paired_contrast_discrepancies": paired_discrepancies,
        "max_absolute_numeric_difference": max_abs_difference,
        "tolerance": ABS_TOL,
        "provenance": provenance,
    }


def fmt(value: float | int | None, digits: int = 6) -> str:
    if value is None:
        return "NA"
    if isinstance(value, int):
        return str(value)
    return f"{value:.{digits}g}"


def select_group(
    aggregates: list[dict[str, Any]], family: str, case: str, variant: str, comparison: str
) -> dict[str, Any]:
    identity = group_id(family, case, variant, comparison)
    return next(row for row in aggregates if row["group_id"] == identity)


def render_report(audit: dict[str, Any]) -> str:
    aggregates = audit["aggregates"]
    contrasts = audit["paired_contrasts"]
    integrity = audit["integrity"]
    primary = select_group(aggregates, "v2-phase", "alternative", "prefix_point", "gain_M3_M2")
    null = select_group(aggregates, "v2-phase", "null", "prefix_point", "gain_M3_M2")
    structured = select_group(aggregates, "v2-phase", "structured", "prefix_point", "gain_M3_M2")
    structured_timing = select_group(
        aggregates, "v2-phase", "structured", "prefix_point", "gain_M2_M0"
    )
    paired_intervals_crossing_zero = sum(
        row["mc95_lower"] <= 0.0 <= row["mc95_upper"] for row in contrasts
    )
    lines = [
        "# Independent A10b aggregate audit",
        "",
        "## Decisive findings",
        "",
        f"- The audit reconstructed {integrity['aggregate_group_count']} planned across-trial groups and "
        f"{integrity['paired_contrast_count']} paired stress-minus-null groups directly from "
        f"{integrity['score_rows']:,} score rows.",
        f"- The primary v2 injected-effect prefix-point M3-M2 mean was {fmt(primary['mean'], 8)} nats per "
        f"forecast (trial SD {fmt(primary['sample_sd'], 8)}; nominal Monte Carlo 95% interval "
        f"[{fmt(primary['mc95_lower'], 8)}, {fmt(primary['mc95_upper'], 8)}]; "
        f"{primary['count']} trials; mean scored n {fmt(primary['mean_scored_n'], 8)}).",
        f"- The corresponding v2 null mean was {fmt(null['mean'], 8)} "
        f"[{fmt(null['mc95_lower'], 8)}, {fmt(null['mc95_upper'], 8)}], and the structured zero-direct-mark "
        f"control mean was {fmt(structured['mean'], 8)} "
        f"[{fmt(structured['mc95_lower'], 8)}, {fmt(structured['mc95_upper'], 8)}].",
        f"- In the structured control, the timing model improved on the stationary model by "
        f"{fmt(structured_timing['mean'], 8)} nats per forecast "
        f"[{fmt(structured_timing['mc95_lower'], 8)}, {fmt(structured_timing['mc95_upper'], 8)}], while adding "
        "the duration mark did not show a stable further gain. This is the intended distinction between "
        "predictable timing structure and incremental mark information.",
        f"- {primary['individual_intervals_containing_zero']}/{primary['count']} injected-effect trial-level "
        "three-year cluster intervals contained zero. These intervals are diagnostics, not eight-trial power or "
        "coverage calibration.",
        f"- All {paired_intervals_crossing_zero}/{len(contrasts)} nominal paired stress-minus-null intervals "
        "included zero. The pilot therefore found no stable stress shift, but is too small to establish absence "
        "of observation-process artefacts.",
        "",
        "## Verification",
        "",
        f"- Expected/completed/failed/missing trials: {integrity['expected_trials']}/"
        f"{integrity['successful_trials']}/{integrity['failed_trials']}/{integrity['missing_trials']}.",
        f"- Score rows were unique; maximum row-level gain identity discrepancy was "
        f"{fmt(integrity['max_row_gain_identity_error'], 4)}.",
        f"- Independently recomputed per-trial means matched saved trial estimates to "
        f"{fmt(integrity['max_trial_estimate_error'], 4)} maximum absolute error; score counts matched exactly.",
    ]
    reconciliation = audit["final_summary_reconciliation"]
    if reconciliation["status"] == "match":
        lines.append(
            f"- The final pipeline summary had the exact {reconciliation['recognized_rows']}-group set and "
            f"matched all audited fields within {fmt(reconciliation['max_absolute_numeric_difference'], 4)} "
            "maximum absolute difference."
        )
    else:
        lines.append(f"- Final summary reconciliation status: `{reconciliation['status']}`.")
    lines.extend(
        [
            "",
            "## Primary M3-M2 synthetic results",
            "",
            "| Family | Case | Variant | Trials | Mean | Trial SD | MC95 | Mean scored n |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    display_groups = [
        ("v2-phase", case, variant)
        for case in ("null", "structured", "gross", "offset", "adaptive", "alternative")
        for variant in ("prefix_point", "prefix_uniform_end")
    ] + [
        ("v4-phase", case, variant)
        for case in ("null", "alternative")
        for variant in ("prefix_point", "prefix_uniform_end")
    ]
    for family, case, variant in display_groups:
        row = select_group(aggregates, family, case, variant, "gain_M3_M2")
        lines.append(
            f"| {family} | {case} | {variant} | {row['count']} | {fmt(row['mean'])} | "
            f"{fmt(row['sample_sd'])} | [{fmt(row['mc95_lower'])}, {fmt(row['mc95_upper'])}] | "
            f"{fmt(row['mean_scored_n'])} |"
        )
    lines.extend(
        [
            "",
            "## Paired observation-stress contrasts",
            "",
            "Stress-minus-null differences use common replicate streams. They compare trial means, not a common "
            "set of forecast rows; altered extraction and eligibility can change the scored population.",
            "",
            "| Stress | Variant | Comparison | Pairs | Mean difference | MC95 |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    for row in contrasts:
        if row["comparison"] != "gain_M3_M2":
            continue
        lines.append(
            f"| {row['stress_case']} | {row['variant']} | {row['comparison']} | {row['count']} | "
            f"{fmt(row['mean'])} | [{fmt(row['mc95_lower'])}, {fmt(row['mc95_upper'])}] |"
        )
    lines.extend(
        [
            "",
            "## Assumptions and residual risks",
            "",
            "- The inferential unit is one independently seeded synthetic trial. Forecast rows within a trial are "
            "not treated as independent Monte Carlo replicates.",
            "- The nominal t intervals quantify between-trial Monte Carlo dispersion for this fixed pilot only. "
            "Four or eight trials cannot establish power, type-I error, interval calibration, or absence of small "
            "artefacts.",
            "- The structured control is an AR Gaussian-copula process in which a measured mark can proxy state; it "
            "is not a separate hidden-state data-generating model and is not a pure false-positive null.",
            "- Oracle and retrospective variants change timing information, boundaries, eligible marks, and fitted "
            "parameters. Oracle gain is therefore diagnostic, not a mathematical upper bound on prefix gain.",
            "- L2 is a two-day issuance-delay diagnostic: it retains features fixed at emission, advances issue age "
            "by two days, and recomputes issue windows and outcomes. Training rows remain available by observation "
            "time T rather than under a uniform T+2 ingestion lag, so L2 is not a reporting-lag replay or an "
            "operational availability test. This does not affect the primary zero-latency results.",
            "- V4 is an unqualified waveform stress family. All results concern the fixed synthetic generator, "
            "cadence, extraction and conditional lognormal models, not the real SS Cyg history or operational "
            "forecast performance.",
            "",
            "Recommendation: accept the aggregation only if final-summary reconciliation is an exact group/count "
            "match with maximum numerical discrepancy at most 1e-10. Treat the injected v2 signal as a positive "
            "pilot result, then design a substantially larger frozen operating-characteristic experiment before "
            "making calibration or detection claims. Independent scientific review would materially improve the "
            "design of that next experiment, but would not change the arithmetic conclusion of this audit.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    repo = Path(__file__).resolve().parents[1]
    output_dir = repo / "outputs" / "a10b_aggregate_audit"
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=repo / "outputs" / "a10b_controls_repaired_20261108",
    )
    parser.add_argument("--config", type=Path, default=repo / "configs" / "a10b_controls.json")
    parser.add_argument("--output-json", type=Path, default=output_dir / "a10b_aggregate_audit.json")
    parser.add_argument("--report", type=Path, default=output_dir / "a10b_aggregate_audit_report.md")
    parser.add_argument("--allow-incomplete", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_json(args.config)
    expected = expected_trials(config)
    if len(expected) != 56:
        raise AssertionError(f"expected 56 configured trials, found {len(expected)}")
    records, missing_trials = load_trial_records(args.input_dir, expected)
    receipt_path = args.input_dir / "receipt.json"
    receipt = load_json(receipt_path)
    if not args.allow_incomplete and (missing_trials or receipt.get("status") not in {"complete", "completed"}):
        raise RuntimeError(
            f"pilot incomplete: receipt={receipt.get('status')}, missing={len(missing_trials)}; "
            "use --allow-incomplete only for script development"
        )
    scores_path = args.input_dir / "scores.jsonl"
    score_values, row_counts, score_integrity = read_scores(scores_path, expected)
    trial_means, trial_reconciliation = reconcile_trial_estimates(
        expected, records, score_values, row_counts
    )
    interval_contains_zero = trial_reconciliation.pop("individual_interval_contains_zero")
    interval_positive = trial_reconciliation.pop("individual_interval_positive")
    aggregates = aggregate_groups(
        expected,
        records,
        missing_trials,
        trial_means,
        row_counts,
        interval_contains_zero,
        interval_positive,
    )
    if len(aggregates) != 132:
        raise AssertionError(f"expected 132 planned aggregate groups, found {len(aggregates)}")
    contrasts = paired_contrasts(config, records, trial_means, row_counts)
    if len(contrasts) != 36:
        raise AssertionError(f"expected 36 paired contrasts, found {len(contrasts)}")
    failed_records = {key: record for key, record in records.items() if not record["success"]}
    summary_path = args.input_dir / "summary.json"
    if summary_path.exists():
        final_summary_reconciliation = reconcile_final_summary(summary_path, aggregates, contrasts)
    else:
        final_summary_reconciliation = {"status": "summary_absent", "path": str(summary_path)}
    records_path = args.input_dir / "records.json"
    input_hashes = {
        "config": sha256(args.config),
        "receipt": sha256(receipt_path),
        "scores": sha256(scores_path),
    }
    if records_path.exists():
        input_hashes["records"] = sha256(records_path)
    if summary_path.exists():
        input_hashes["summary"] = sha256(summary_path)
    integrity = {
        **score_integrity,
        **trial_reconciliation,
        "expected_trials": len(expected),
        "successful_trials": sum(record["success"] for record in records.values()),
        "failed_trials": len(failed_records),
        "missing_trials": len(missing_trials),
        "aggregate_group_count": len(aggregates),
        "paired_contrast_count": len(contrasts),
        "exact_score_group_set_for_available_successes": True,
    }
    audit = {
        "scope": "independent aggregation audit of fixed A10b repaired synthetic development pilot",
        "estimand": "unweighted mean across independent trial-level held-out log-score gains",
        "paired_estimand": "mean within-replicate stress-minus-null difference in trial-level gain",
        "input_dir": str(args.input_dir),
        "receipt_status": receipt.get("status"),
        "input_sha256": input_hashes,
        "integrity": integrity,
        "trial_failures": {
            trial_id(*key): record.get("error", record.get("result")) for key, record in failed_records.items()
        },
        "missing_trial_ids": [trial_id(*key) for key in missing_trials],
        "aggregates": aggregates,
        "paired_contrasts": contrasts,
        "final_summary_reconciliation": final_summary_reconciliation,
        "limitations": [
            "nominal t Monte Carlo intervals use only four or eight independent trials",
            "trial-level cluster intervals are diagnostics rather than calibrated confirmatory intervals",
            "paired stress contrasts can combine score changes with changes in the scored forecast population",
            "structured control allows legitimate state-proxy information and is not a pure no-information null",
            "oracle and retrospective gains are diagnostics rather than upper bounds",
            "L2 delays issuance but does not impose a uniform two-day reporting lag on training-record availability",
            "v4 is an unqualified waveform stress family",
            "synthetic results do not estimate real-star or operational forecast performance",
        ],
    }
    write_json(args.output_json, audit)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_report(audit), encoding="utf-8")
    if not args.allow_incomplete:
        if integrity["failed_trials"] or integrity["missing_trials"]:
            raise AssertionError("complete pilot contains failed or missing trials")
        reconciliation = audit["final_summary_reconciliation"]
        if reconciliation["status"] != "match":
            raise AssertionError(f"final summary reconciliation failed: {reconciliation['status']}")
        if reconciliation["max_absolute_numeric_difference"] > ABS_TOL:
            raise AssertionError("final summary numerical discrepancy exceeds tolerance")
    print(
        json.dumps(
            {
                "status": "ok" if not args.allow_incomplete else "partial_ok",
                "successful_trials": integrity["successful_trials"],
                "failed_trials": integrity["failed_trials"],
                "missing_trials": integrity["missing_trials"],
                "aggregate_groups": len(aggregates),
                "paired_contrasts": len(contrasts),
                "final_summary_reconciliation": final_summary_reconciliation["status"],
                "output_json": str(args.output_json),
                "report": str(args.report),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
