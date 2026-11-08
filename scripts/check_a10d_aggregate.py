#!/usr/bin/env python3
"""Independent audit of the completed A10d operating-characteristic aggregate.

Only serialized records, score streams, the receipt, the summary and the frozen
configuration are read.  This checker does not import candidate OC code.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
from typing import Any


TOL = 1.0e-9
ALPHA = 0.05
NOMINAL_COVERAGE = 0.90
COMPARISON = "gain_M3_M2"
EXPECTED_FAMILIES = {
    "v2-phase": (40, ("null", "structured", "slow_090", "slow_098", "gross", "offset", "adaptive", "alternative")),
    "v4-phase": (20, ("null", "alternative")),
}
NULL_CASES = (
    ("v2-phase", "null"),
    ("v2-phase", "structured"),
    ("v2-phase", "gross"),
    ("v2-phase", "offset"),
    ("v2-phase", "adaptive"),
    ("v4-phase", "null"),
)
REFERENCE_CASES = (("v2-phase", "null"), ("v2-phase", "alternative"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def close(left: Any, right: Any, tolerance: float = TOL) -> bool:
    try:
        return abs(float(left) - float(right)) <= tolerance
    except (TypeError, ValueError):
        return left == right


def beta_continued_fraction(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta, continued-fraction evaluation."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < 3.0e-30:
        d = math.copysign(3.0e-30, d)
    d, h = 1.0 / d, 1.0 / d
    for m in range(1, 10000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < 3.0e-30:
            d = math.copysign(3.0e-30, d)
        c = 1.0 + aa / c
        if abs(c) < 3.0e-30:
            c = math.copysign(3.0e-30, c)
        d, c = 1.0 / d, c
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < 3.0e-30:
            d = math.copysign(3.0e-30, d)
        c = 1.0 + aa / c
        if abs(c) < 3.0e-30:
            c = math.copysign(3.0e-30, c)
        d, c = 1.0 / d, c
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 3.0e-14:
            break
    return h


def regularized_beta(x: float, a: float, b: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    log_front = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                 + a * math.log(x) + b * math.log1p(-x))
    front = math.exp(log_front)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * beta_continued_fraction(a, b, x) / a
    return 1.0 - front * beta_continued_fraction(b, a, 1.0 - x) / b


def student_t_cdf(value: float, degrees: float) -> float:
    if value == 0.0:
        return 0.5
    x = degrees / (degrees + value * value)
    tail = 0.5 * regularized_beta(x, degrees / 2.0, 0.5)
    return 1.0 - tail if value > 0.0 else tail


def student_t_ppf(probability: float, degrees: float) -> float:
    if not 0.0 < probability < 1.0 or degrees <= 0.0:
        raise ValueError("invalid Student-t quantile request")
    sign = 1.0 if probability >= 0.5 else -1.0
    target = probability if sign > 0 else 1.0 - probability
    lo, hi = 0.0, 1.0
    while student_t_cdf(hi, degrees) < target:
        hi *= 2.0
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if student_t_cdf(mid, degrees) < target:
            lo = mid
        else:
            hi = mid
    return sign * (lo + hi) / 2.0


def binomial_cdf(k: int, n: int, probability: float) -> float:
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    terms = [math.comb(n, i) * probability**i * (1.0 - probability)**(n - i)
             for i in range(k + 1)]
    return sum(terms)


def one_sided_binomial_upper95(successes: int, total: int) -> float:
    if total <= 0:
        return None
    if successes >= total:
        return 1.0
    if successes == 0:
        return 1.0 - ALPHA ** (1.0 / total)
    lo, hi = 0.0, 1.0
    # Solve P_p(X <= successes) = .05 for the one-sided 95% upper bound.
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if binomial_cdf(successes, total, mid) > ALPHA:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def exact_binomial_summary(successes: int, total: int) -> dict[str, Any]:
    rate = successes / total if total else None
    # Equal-tailed exact interval by inverting the binomial CDF.  The lower
    # and upper values are diagnostics; the gate uses the one-sided upper.
    if successes == 0:
        lower = 0.0
    else:
        lo, hi = 0.0, 1.0
        for _ in range(100):
            mid = (lo + hi) / 2.0
            if binomial_cdf(successes - 1, total, mid) > 1.0 - ALPHA / 2.0:
                lo = mid
            else:
                hi = mid
        lower = (lo + hi) / 2.0
    if successes == total:
        upper = 1.0
    else:
        lo, hi = 0.0, 1.0
        for _ in range(100):
            mid = (lo + hi) / 2.0
            if binomial_cdf(successes, total, mid) > ALPHA / 2.0:
                lo = mid
            else:
                hi = mid
        upper = (lo + hi) / 2.0
    return {
        "successes": successes,
        "total": total,
        "rate": rate,
        "mc_se": math.sqrt(rate * (1.0 - rate) / total) if total else None,
        "exact_lower95": lower,
        "exact_upper95": upper,
        "one_sided_upper95": one_sided_binomial_upper95(successes, total),
    }


def primary_interval(rows: list[dict[str, Any]], origin: float, years: int = 6) -> dict[str, Any]:
    if not rows:
        raise ValueError("no primary score rows")
    width = years * 365.25
    grouped: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        issue = float(row["issue_time"])
        index = math.floor((issue - origin) / width)
        grouped[index].append(float(row["M3"]) - float(row["M2"]))
    if min(grouped) < 0 or set(grouped) != set(range(max(grouped) + 1)):
        raise ValueError("evaluation issue times do not form contiguous origin-anchored clusters")
    counts = [len(grouped[index]) for index in sorted(grouped)]
    means = [sum(grouped[index]) / len(grouped[index]) for index in sorted(grouped)]
    total = sum(counts)
    estimate = sum(value for group in grouped.values() for value in group) / total
    blocks = len(means)
    se = math.sqrt(blocks * sum((count * (mean - estimate)) ** 2
                                for count, mean in zip(counts, means))
                   / (total * total * (blocks - 1))) if blocks > 1 else math.nan
    critical = student_t_ppf(0.95, blocks - 1)
    lower, upper = estimate - critical * se, estimate + critical * se
    return {
        "blocks": blocks,
        "n": total,
        "estimate": estimate,
        "se": se,
        "lower": lower,
        "upper": upper,
        "confirmed": lower > 0.0,
        "origin": origin,
        "years": years,
        "cluster_counts": counts,
    }


def first_present(mapping: dict[str, Any], names: tuple[str, ...]) -> Any:
    for name in names:
        if name in mapping:
            return mapping[name]
    return None


def extract_reference_means(reference: dict[str, Any]) -> list[float] | None:
    value = first_present(reference, ("reference_means", "reference_values", "replica_means", "means"))
    if value is None:
        return None
    if not isinstance(value, list):
        return None
    return [float(x) for x in value]


def reference_interval(candidate: dict[str, Any], means: list[float], analytic_zero: bool) -> dict[str, Any]:
    if len(means) != 6:
        raise ValueError(f"expected six reference means, got {len(means)}")
    reference_mean = sum(means) / len(means)
    reference_se = math.sqrt(sum((x - reference_mean) ** 2 for x in means) / (len(means) - 1)) / math.sqrt(len(means))
    candidate_se = float(candidate["se"])
    candidate_df = int(candidate["blocks"]) - 1
    difference = float(candidate["estimate"]) - reference_mean
    variance = candidate_se**2 + reference_se**2
    if variance == 0.0:
        lower = upper = difference
        welch_df = math.inf
    else:
        welch_df = ((candidate_se**2 + reference_se**2) ** 2 /
                    ((candidate_se**4 / candidate_df) +
                     (reference_se**4 / (len(means) - 1))))
        critical = student_t_ppf(0.95, welch_df)
        half_width = critical * math.sqrt(variance)
        lower, upper = difference - half_width, difference + half_width
    return {
        "reference_mean": reference_mean,
        "reference_se": reference_se,
        "difference": difference,
        "welch_df": welch_df,
        "lower": lower,
        "upper": upper,
        "joint_mc_covers_zero": lower <= 0.0 <= upper,
        "analytic_zero": analytic_zero,
    }


def analytic_zero_interval(candidate: dict[str, Any]) -> dict[str, Any]:
    """Exact β=0 identity: no six-replica continuation is needed."""
    estimate = float(candidate["estimate"])
    return {
        "reference_mean": 0.0,
        "reference_se": 0.0,
        "difference": estimate,
        "welch_df": math.inf,
        "lower": estimate,
        "upper": estimate,
        "joint_mc_covers_zero": estimate == 0.0,
        "analytic_zero": True,
    }


def frozen_primary_beta(record: dict[str, Any]) -> float | None:
    try:
        value = record["result"]["models"]["primary"]["models"]["M3"]["coefficients"]["beta"]
        return float(value)
    except (KeyError, TypeError, ValueError):
        return None


def compare_interval(saved: dict[str, Any], calculated: dict[str, Any], failures: list[dict[str, Any]], context: str) -> None:
    for field in ("blocks", "n", "estimate", "se", "lower", "upper", "confirmed", "origin", "years"):
        if field not in saved:
            failures.append({"kind": "missing_interval_field", "context": context, "field": field})
        elif field == "confirmed":
            if bool(saved[field]) != bool(calculated[field]):
                failures.append({"kind": "interval_mismatch", "context": context, "field": field,
                                 "saved": saved[field], "calculated": calculated[field]})
        elif not close(saved[field], calculated[field]):
            failures.append({"kind": "interval_mismatch", "context": context, "field": field,
                             "saved": saved[field], "calculated": calculated[field]})


def task_grid() -> set[tuple[str, str, int]]:
    return {(family, case, replicate)
            for family, (replicates, cases) in EXPECTED_FAMILIES.items()
            for case in cases for replicate in range(replicates)}


def audit(directory: Path) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    receipt_path, records_path, summary_path = (directory / name for name in ("receipt.json", "records.json", "summary.json"))
    files = sorted(directory.glob("*-scores.jsonl"))
    report: dict[str, Any] = {"directory": str(directory), "files": [str(path) for path in files]}
    if not receipt_path.exists() or not records_path.exists():
        failures.append({"kind": "missing_required_file", "files": [str(path) for path in (receipt_path, records_path) if not path.exists()]})
        report["audit_failures"] = failures
        return report
    receipt = json.loads(receipt_path.read_text())
    records = json.loads(records_path.read_text())
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else None
    report["input_sha256"] = {"receipt": sha256(receipt_path), "records": sha256(records_path),
                               **{path.name: sha256(path) for path in files}}
    report["receipt_status"] = receipt.get("status")
    if receipt.get("status") != "completed":
        failures.append({"kind": "receipt_not_completed", "status": receipt.get("status")})
    if receipt.get("failed_trials", 0) != 0:
        failures.append({"kind": "failed_trials", "count": receipt.get("failed_trials")})
    if receipt.get("records_sha256") != sha256(records_path):
        failures.append({"kind": "records_hash_mismatch"})
    listed_hashes = receipt.get("files_sha256", {})
    for name, expected in listed_hashes.items():
        path = directory / name
        if not path.exists():
            failures.append({"kind": "receipt_file_missing", "file": name})
        elif sha256(path) != expected:
            failures.append({"kind": "receipt_file_hash_mismatch", "file": name})
    if receipt.get("summary_sha256") is not None:
        if not summary_path.exists() or receipt["summary_sha256"] != sha256(summary_path):
            failures.append({"kind": "summary_hash_mismatch"})
    listed_scores = {name for name in listed_hashes if name.endswith("-scores.jsonl")}
    discovered_scores = {path.name for path in files}
    if listed_scores != discovered_scores:
        failures.append({"kind": "score_file_inventory_mismatch", "listed": sorted(listed_scores),
                         "discovered": sorted(discovered_scores)})

    expected_tasks = task_grid()
    task_records: dict[tuple[str, str, int], dict[str, Any]] = {}
    for index, record in enumerate(records):
        task = tuple(record.get("task", ()))
        if len(task) != 3 or task in task_records:
            failures.append({"kind": "record_task_identity", "index": index, "task": list(task)})
            continue
        if task not in expected_tasks:
            failures.append({"kind": "unexpected_record_task", "task": list(task)})
        task_records[task] = record
        if record.get("success") is not True:
            failures.append({"kind": "record_not_successful", "task": list(task)})
    if set(task_records) != expected_tasks:
        failures.append({"kind": "exact360_task_grid", "expected": len(expected_tasks),
                         "observed": len(task_records), "missing": [list(x) for x in sorted(expected_tasks - set(task_records))[:10]],
                         "extra": [list(x) for x in sorted(set(task_records) - expected_tasks)[:10]]})

    score_tasks: dict[tuple[str, str, int], list[dict[str, Any]]] = defaultdict(list)
    score_row_errors = 0
    score_id_errors = 0
    score_files_by_task: Counter[tuple[str, str, int]] = Counter()
    for path in files:
        try:
            rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        except Exception as exc:
            failures.append({"kind": "score_json_error", "file": path.name, "error": str(exc)})
            continue
        seen_ids: set[tuple[str, str, int, str, int]] = set()
        local_tasks: set[tuple[str, str, int]] = set()
        for row in rows:
            task = (row.get("family"), row.get("case"), row.get("replicate"))
            variant = row.get("variant")
            emission = row.get("emission_index")
            identifier = (*task, variant, emission)
            if identifier in seen_ids:
                score_id_errors += 1
            seen_ids.add(identifier)
            local_tasks.add(task)
            for field in ("M0", "M2", "M3", "P3", "gain_M2_M0", "gain_M3_M2", "gain_M3_P3", "gain_P3_M2", "issue_time"):
                if not finite(row.get(field)):
                    score_row_errors += 1
            score_tasks[task].append(row)
        for task in local_tasks:
            score_files_by_task[task] += 1
    if score_row_errors:
        failures.append({"kind": "nonfinite_score_fields", "count": score_row_errors})
    if score_id_errors:
        failures.append({"kind": "duplicate_score_ids", "count": score_id_errors})
    for task in expected_tasks:
        if task not in score_tasks:
            failures.append({"kind": "missing_score_task", "task": list(task)})
        elif score_files_by_task[task] != 1:
            failures.append({"kind": "score_task_file_count", "task": list(task), "files": score_files_by_task[task]})
    for task in sorted(set(score_tasks) - expected_tasks):
        failures.append({"kind": "unexpected_score_task", "task": list(task)})

    interval_failures = 0
    case_records: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    reference_records: list[dict[str, Any]] = []
    trial_summaries: list[dict[str, Any]] = []
    for task, record in task_records.items():
        result = record.get("result", {})
        family, case, replicate = task
        case_records[(family, case)].append(record)
        if family == "v2-phase" and case in ("null", "alternative"):
            reference_records.append(record)
        origin = result.get("stream_metadata", {}).get("training_cutoff")
        rows = [row for row in score_tasks.get(task, []) if row.get("variant") == "primary"]
        ids = [row.get("emission_index") for row in rows]
        if len(ids) != len(set(ids)):
            failures.append({"kind": "primary_score_id_duplicate", "task": list(task)})
        try:
            calculated = primary_interval(rows, float(origin), 6)
            saved = result["intervals"]["primary"]["6"][COMPARISON]
            before = len(failures)
            compare_interval(saved, calculated, failures, f"{family}/{case}/{replicate}")
            interval_failures += len(failures) - before
            trial_summaries.append({"task": list(task), "estimate": calculated["estimate"],
                                    "se": calculated["se"], "lower": calculated["lower"],
                                    "confirmed": calculated["confirmed"], "n": calculated["n"],
                                    "blocks": calculated["blocks"]})
        except Exception as exc:
            failures.append({"kind": "primary_interval_error", "task": list(task), "error": str(exc)})

    reference_results: list[dict[str, Any]] = []
    for record in reference_records:
        task = tuple(record["task"])
        ref_all = record.get("result", {}).get("reference_calibration")
        if not isinstance(ref_all, dict):
            failures.append({"kind": "missing_reference_record", "task": list(task)})
            continue
        ref = ref_all.get("6")
        if not isinstance(ref, dict):
            failures.append({"kind": "missing_reference_year", "task": list(task), "year": 6})
            continue
        method = ref.get("method")
        beta = frozen_primary_beta(record)
        if method not in ("analytic_zero_identity", "matched_58y_replicas_joint_mc"):
            failures.append({"kind": "unknown_reference_method", "task": list(task), "method": method})
            continue
        if beta is None or not math.isfinite(beta):
            failures.append({"kind": "missing_frozen_beta", "task": list(task)})
            continue
        means = extract_reference_means(ref)
        analytic_zero = method == "analytic_zero_identity"
        if analytic_zero and beta != 0.0:
            failures.append({"kind": "analytic_zero_beta_mismatch", "task": list(task), "beta": beta})
        if not analytic_zero and beta == 0.0:
            failures.append({"kind": "matched_reference_zero_beta", "task": list(task)})
        if means is None:
            failures.append({"kind": "missing_reference_means", "task": list(task)})
            continue
        if analytic_zero and means:
            failures.append({"kind": "analytic_zero_reference_means_not_empty", "task": list(task),
                             "count": len(means)})
            continue
        if not analytic_zero and len(means) != 6:
            failures.append({"kind": "reference_mean_count", "task": list(task), "count": len(means)})
            continue
        if means is not None and any(not math.isfinite(value) for value in means):
            failures.append({"kind": "nonfinite_reference_mean", "task": list(task)})
            continue
        try:
            candidate = next(item for item in trial_summaries if item["task"] == list(task))
            expected_interior = beta != 0.0
            if "interior" not in ref:
                failures.append({"kind": "missing_reference_interior", "task": list(task)})
            elif bool(ref["interior"]) != expected_interior:
                failures.append({"kind": "reference_interior_mismatch", "task": list(task),
                                 "saved": ref["interior"], "calculated": expected_interior})
            if analytic_zero and (candidate["estimate"] != 0.0 or candidate["se"] != 0.0):
                failures.append({"kind": "analytic_zero_candidate_not_exact", "task": list(task),
                                 "estimate": candidate["estimate"], "se": candidate["se"]})
            calculated = analytic_zero_interval(candidate) if analytic_zero else reference_interval(candidate, means, False)
            actual_fields = {
                "reference_mean": calculated["reference_mean"],
                "reference_se": calculated["reference_se"],
                "difference": calculated["difference"],
                "joint_mc_df": calculated["welch_df"],
                "joint_mc_lower": calculated["lower"],
                "joint_mc_upper": calculated["upper"],
                "joint_mc_covers_zero": calculated["joint_mc_covers_zero"],
            }
            if not analytic_zero:
                required_fields = ("reference_mean", "reference_se", "difference",
                                   "joint_mc_df", "joint_mc_lower", "joint_mc_upper",
                                   "joint_mc_covers_zero")
                for field in required_fields:
                    if field not in ref:
                        failures.append({"kind": "missing_reference_interval_field", "task": list(task),
                                         "field": field})
            elif "joint_mc_covers_zero" not in ref:
                failures.append({"kind": "missing_reference_coverage_flag", "task": list(task)})
            for field, expected in actual_fields.items():
                if field not in ref:
                    continue
                if field == "joint_mc_covers_zero":
                    equal = bool(ref[field]) == bool(expected)
                elif math.isinf(float(ref[field])) and math.isinf(float(expected)):
                    equal = True
                else:
                    equal = close(ref[field], expected)
                if not equal:
                    failures.append({"kind": "reference_interval_mismatch", "task": list(task),
                                     "field": field, "saved": ref[field], "calculated": expected})
            interior = expected_interior
            reference_results.append({"task": list(task), "case": task[1], "interior": interior,
                                      "method": method, "analytic_zero": analytic_zero, **calculated})
        except Exception as exc:
            failures.append({"kind": "reference_interval_error", "task": list(task), "error": str(exc)})
    if len(reference_records) != 80:
        failures.append({"kind": "reference_record_count", "expected": 80, "observed": len(reference_records)})
    if len(reference_results) != len(reference_records):
        failures.append({"kind": "reference_reconciliation_count", "expected": len(reference_records), "observed": len(reference_results)})

    null_checks: list[dict[str, Any]] = []
    for family, case in NULL_CASES:
        trials = case_records.get((family, case), [])
        confirmed = sum(bool(next((item for item in trial_summaries if item["task"] == list(r["task"])), {}).get("confirmed", False)) for r in trials)
        check = exact_binomial_summary(confirmed, len(trials))
        check.update({"family": family, "case": case, "screen_pass": bool(len(trials) and check["rate"] <= 0.05),
                      "certification_pass": bool(len(trials) and check["one_sided_upper95"] <= 0.05)})
        null_checks.append(check)
    if len(null_checks) != 6 or any(check["total"] == 0 for check in null_checks):
        failures.append({"kind": "null_case_grid", "checks": null_checks})

    calibration: list[dict[str, Any]] = []
    for case in ("null", "alternative"):
        entries = [entry for entry in reference_results if entry["case"] == case]
        for population, selected in (("overall", entries), ("interior", [e for e in entries if e["interior"]])):
            successes = sum(bool(e["joint_mc_covers_zero"]) for e in selected)
            total = len(selected)
            p_value = binomial_cdf(successes, total, NOMINAL_COVERAGE) if total else None
            calibration.append({"family": "v2-phase", "case": case, "population": population,
                                "successes": successes, "total": total,
                                "lower_tail_p": p_value,
                                "tested": bool(total),
                                "pass": (p_value > ALPHA) if total else None})
    coverage_pass = all(item["pass"] is not False for item in calibration if item["tested"])
    complete = (set(task_records) == expected_tasks and not any(not r.get("success") for r in task_records.values())
                and len(files) == 360 and not score_row_errors and not score_id_errors
                and interval_failures == 0 and len(reference_results) == 80)
    screen_pass = complete and all(item["screen_pass"] for item in null_checks) and coverage_pass
    formal_pass = complete and all(item["certification_pass"] for item in null_checks) and coverage_pass
    computed = {"complete": complete, "screen_pass": screen_pass,
                "formal_certification_pass": formal_pass, "real_fit_automatic": False,
                "null_rate_checks": null_checks, "calibration": calibration}
    if summary is None:
        failures.append({"kind": "missing_summary"})
    else:
        for field in ("complete", "screen_pass", "formal_certification_pass"):
            if field in summary and bool(summary[field]) != bool(computed[field]):
                failures.append({"kind": "summary_decision_mismatch", "field": field,
                                 "saved": summary[field], "calculated": computed[field]})
        if "real_fit_automatic" in summary and bool(summary["real_fit_automatic"]):
            failures.append({"kind": "summary_real_fit_automatic_true"})
        if "null_rate_checks" in summary and len(summary["null_rate_checks"]) != 6:
            failures.append({"kind": "summary_null_check_count", "observed": len(summary["null_rate_checks"])})
        else:
            summary_checks = {(item.get("family"), item.get("case")): item
                              for item in summary.get("null_rate_checks", [])
                              if isinstance(item, dict)}
            for calculated_check in null_checks:
                saved_check = summary_checks.get((calculated_check["family"], calculated_check["case"]))
                if saved_check is None:
                    failures.append({"kind": "summary_null_case_missing", "case": calculated_check["case"],
                                     "family": calculated_check["family"]})
                    continue
                for field, aliases in (("successes", ("successes", "rejections", "count")),
                                       ("total", ("total", "n")),
                                       ("rate", ("rate",))):
                    saved_value = first_present(saved_check, aliases)
                    if saved_value is not None and not close(saved_value, calculated_check[field]):
                        failures.append({"kind": "summary_null_case_mismatch",
                                         "case": calculated_check["case"], "family": calculated_check["family"],
                                         "field": field, "saved": saved_value,
                                         "calculated": calculated_check[field]})
                for field in ("screen_pass", "certification_pass"):
                    if field in saved_check and bool(saved_check[field]) != bool(calculated_check[field]):
                        failures.append({"kind": "summary_null_case_mismatch",
                                         "case": calculated_check["case"], "family": calculated_check["family"],
                                         "field": field, "saved": saved_check[field],
                                         "calculated": calculated_check[field]})
        saved_calibration = summary.get("calibration")
        if isinstance(saved_calibration, list):
            saved_calibration_map = {(item.get("case"), item.get("population"), item.get("cluster_years", item.get("years", 6))): item
                                     for item in saved_calibration if isinstance(item, dict)}
            for calculated_item in calibration:
                key = (calculated_item["case"], calculated_item["population"], 6)
                saved_item = saved_calibration_map.get(key)
                if saved_item is None:
                    continue
                if "pass" in saved_item and saved_item["pass"] is not None and bool(saved_item["pass"]) != bool(calculated_item["pass"]):
                    failures.append({"kind": "summary_calibration_mismatch", "key": list(key),
                                     "saved": saved_item["pass"], "calculated": calculated_item["pass"]})
    report.update({"records": len(records), "scores": len(files), "computed": computed,
                   "trial_interval_count": len(trial_summaries),
                   "reference_record_count": len(reference_results),
                   "reference_method_counts": dict(Counter(item["method"] for item in reference_results)),
                   "audit_failures": failures})
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = audit(args.directory)
    except Exception as exc:  # Preserve a machine-readable failure report.
        report = {"directory": str(args.directory), "audit_failures": [{"kind": "fatal", "error": str(exc)}]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"directory": str(args.directory), "audit_failures": len(report.get("audit_failures", [])),
                      "screen_pass": report.get("computed", {}).get("screen_pass"),
                      "formal_certification_pass": report.get("computed", {}).get("formal_certification_pass")}))
    if report.get("audit_failures"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
