#!/usr/bin/env python3
"""Source-independent score reconciliation for one completed A10b trial.

The script reads only the persisted trial result and score stream.  It rebuilds
the lognormal landmark likelihood from model metadata, ledger endpoints and
evidence bounds; it does not import the project scoring implementation.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, stdev
from typing import Any

try:
    from scipy.special import log_ndtr as scipy_log_ndtr
    from scipy.stats import t as student_t
except ImportError:  # pragma: no cover - the project audit environment has scipy
    scipy_log_ndtr = None
    student_t = None


SQRT2 = math.sqrt(2.0)
LOG_SQRT_2PI = 0.5 * math.log(2.0 * math.pi)
EPS = 1.0e-12


def log_ndtr(x: float) -> float:
    """Stable log normal CDF, using direct erfc through the safe tail."""
    if -32.0 <= x <= 0.0:
        return math.log(0.5 * math.erfc(-x / SQRT2))
    if x < -32.0:
        # Mills expansion; the direct erfc branch avoids its material error at
        # moderate tails (the audit explicitly checks -8, -12 and -30).
        inv = 1.0 / (x * x)
        series = (1.0 - inv + 3.0 * inv ** 2 - 15.0 * inv ** 3
                  + 105.0 * inv ** 4 - 945.0 * inv ** 5
                  + 10395.0 * inv ** 6 - 135135.0 * inv ** 7)
        return -0.5 * x * x - math.log(-x) - LOG_SQRT_2PI + math.log(series)
    # Use the upper-tail complement for positive x; evaluating erfc(-x) and
    # subtracting from two loses the tiny tail that interval differences need.
    return math.log1p(-0.5 * math.erfc(x / SQRT2))


def logdiffexp(log_hi: float, log_lo: float) -> float:
    if log_lo == -math.inf:
        return log_hi
    if log_lo >= log_hi:
        raise ValueError("interval probability is not positive")
    return log_hi + math.log(-math.expm1(log_lo - log_hi))


def lognormal_cdf(value: float, mu: float, sigma: float) -> float:
    if value <= 0.0:
        return -math.inf
    return log_ndtr((math.log(value) - mu) / sigma)


def lognormal_sf(value: float, mu: float, sigma: float) -> float:
    if value <= 0.0:
        return 0.0
    return log_ndtr(-(math.log(value) - mu) / sigma)


def logsumexp(values: list[float]) -> float:
    top = max(values)
    return top + math.log(sum(math.exp(value - top) for value in values))


def endpoint_nodes(feature: dict[str, Any], endpoint_mode: str, nodes: int) -> list[float] | None:
    issue = float(feature["issue_time"])
    if endpoint_mode == "point":
        end = feature.get("end_t")
        return None if end is None else [float(end)]
    lo, hi = feature.get("end_lo"), feature.get("end_hi")
    if lo is None or hi is None:
        return None
    lo, hi = float(lo), min(float(hi), issue)
    if hi < lo - EPS:
        return None
    if hi - lo <= EPS or nodes == 1:
        return [lo]
    return [lo + (hi - lo) * i / (nodes - 1) for i in range(nodes)]


def duration_nodes(feature: dict[str, Any], nodes: list[float] | None) -> list[float] | None:
    if nodes is None:
        return None
    onset = feature.get("onset_t")
    if onset is not None:
        onset = float(onset)
        durations = [node - onset for node in nodes]
        return durations if all(duration > 0.0 for duration in durations) else None
    stored = feature.get("duration")
    if stored is None or float(stored) <= 0.0:
        return None
    return [float(stored)] * len(nodes)


def route_for(name: str, feature: dict[str, Any], endpoint_available: bool,
              duration_available: bool) -> str:
    duration = duration_available
    previous = feature.get("previous_gap_covered") is True and feature.get("previous_gap") is not None
    if not endpoint_available:
        return "R0"
    if name == "M0":
        return "M0"
    if name == "M1":
        return "M1" if duration else "M0"
    if name == "M2":
        return "M2" if previous else "M0"
    if duration and previous:
        return "M3"
    if duration:
        return "M1"
    if previous:
        return "M2"
    return "M0"


def conditional_score(feature: dict[str, Any], evidence: dict[str, Any],
                       spec: dict[str, Any], route: str) -> float:
    issue = float(feature["issue_time"])
    if route == "R0":
        model = spec["r0"]
        nodes = [None]
    else:
        model = spec["models"][route]
        nodes = endpoint_nodes(feature, spec["endpoint_mode"], int(spec["nodes"]))
        if nodes is None:
            raise ValueError(f"{route} selected without endpoint")

    numerators: list[float] = []
    denominators: list[float] = []
    for endpoint in nodes:
        if endpoint is None:
            age = 0.0
        else:
            age = issue - endpoint
            if age < -EPS:
                raise ValueError("endpoint follows issue")
        values: dict[str, float] = {}
        if "duration" in model["terms"] or "duration_type" in model["terms"]:
            onset = feature.get("onset_t")
            if endpoint is None:
                raise ValueError("duration term lacks endpoint")
            if onset is None:
                duration = float(feature["duration"])
            else:
                duration = endpoint - float(onset)
                if duration <= 0.0:
                    raise ValueError("duration must be positive")
            if "duration_type" in model["terms"]:
                duration_type = float(duration >= 12.0)
                centers = model["centers"].get("duration_type")
                if centers is None:
                    centers = model["centers"].get("duration_type_centers")
                if centers is None:
                    raise ValueError("type-within model lacks duration-type centers")
                center = centers[str(int(duration_type))]
                values["duration_type"] = duration_type
                values["duration_within"] = (math.log(duration) - center)
                values["duration_within"] /= model["scales"]["duration_within"]
            else:
                values["duration"] = (math.log(duration) - model["centers"]["duration"])
                values["duration"] /= model["scales"]["duration"]
        if "previous_gap" in model["terms"]:
            previous = feature.get("previous_gap")
            if feature.get("previous_gap_covered") is not True or previous is None:
                raise ValueError("previous-gap term lacks a covered positive gap")
            previous = float(previous)
            if previous <= 0.0:
                raise ValueError("previous gap must be positive")
            values["previous_gap"] = (math.log(previous) - model["centers"]["previous_gap"])
            values["previous_gap"] /= model["scales"]["previous_gap"]
        mu = float(model["intercept"])
        for term, coefficient in model["coefficients"].items():
            mu += float(coefficient) * values[term]
        sigma = float(model["sigma"])
        if evidence["kind"] == "interval":
            lower = max(float(evidence["onset_lo"]), issue) - (endpoint or issue)
            upper = float(evidence["onset_hi"]) - (endpoint or issue)
            numerators.append(logdiffexp(lognormal_cdf(upper, mu, sigma),
                                         lognormal_cdf(lower, mu, sigma)))
        elif evidence["kind"] == "right_censored":
            censor = float(evidence["censor_at"]) - (endpoint or issue)
            numerators.append(lognormal_sf(censor, mu, sigma))
        else:
            raise ValueError(f"unsupported evidence kind {evidence['kind']}")
        denominators.append(lognormal_sf(age, mu, sigma))

    if len(numerators) == 1:
        return numerators[0] - denominators[0]
    return logsumexp(numerators) - logsumexp(denominators)


def independent_cluster_interval(rows: list[dict[str, Any]], metric: str,
                                  stream_metadata: dict[str, Any]) -> dict[str, Any]:
    """Three-year time clusters from the first evaluation stream block."""
    if student_t is None:
        raise RuntimeError("scipy is required for the t interval audit")
    # Clusters are anchored at the first issued evaluation forecast.  This
    # preserves the actual issue-time alignment after the synthetic seam.
    evaluation_start = min(float(row["issue_time"]) for row in rows)
    width = 3.0 * 365.25
    groups = []
    for index in range(20):
        lower, upper = evaluation_start + index * width, evaluation_start + (index + 1) * width
        group = [float(row[metric]) for row in rows if lower <= float(row["issue_time"]) < upper]
        if not group:
            raise ValueError(f"empty three-year cluster {index}")
        groups.append(group)
    block_means = [mean(group) for group in groups]
    counts = [len(group) for group in groups]
    estimate = mean(float(row[metric]) for row in rows)
    # Cluster means represent unequal numbers of forecasts.  The frozen
    # diagnostic uses the finite-cluster correction on n_b-weighted means:
    # B * sum[n_b^2 (m_b - m)^2] / [N^2 (B - 1)].
    n_total = sum(counts)
    n_blocks = len(block_means)
    se = math.sqrt(n_blocks * sum((count * (block_mean - estimate)) ** 2
                                  for count, block_mean in zip(counts, block_means))
                   / (n_total * n_total * (n_blocks - 1)))
    critical = float(student_t.ppf(0.975, n_blocks - 1))
    return {
        "blocks": len(block_means),
        "n": len(rows),
        "estimate": estimate,
        "se": se,
        "lower": estimate - critical * se,
        "upper": estimate + critical * se,
        "cluster_start": evaluation_start,
        "cluster_width": width,
    }


def numerical_fixture_check() -> dict[str, Any]:
    points = [-8.0, -12.0, -30.0, -50.0, 12.0]
    if scipy_log_ndtr is None:
        return {"points": points, "max_abs_error": math.inf, "available": False}
    errors = [abs(log_ndtr(point) - float(scipy_log_ndtr(point))) for point in points]
    return {"points": points, "max_abs_error": max(errors), "available": True}


def audit_trial(path: Path, scores_path: Path,
                scores_kind: str = "growing-stream snapshot") -> dict[str, Any]:
    payload = json.loads(path.read_text())
    if payload.get("success") is not True:
        raise ValueError(f"trial is not complete: {path}")
    result = payload["result"]
    family, case, replicate = result["family"], result["case"], result["replicate"]
    raw_scores = [json.loads(line) for line in scores_path.read_text().splitlines() if line.strip()]
    scored = [row for row in raw_scores if row["family"] == family and row["case"] == case
              and row["replicate"] == replicate]
    expected_by_variant = {variant: {row["emission_index"]: row for row in scored
                                     if row["variant"] == variant}
                           for variant in result["models"]}
    max_error = 0.0
    error_count = 0
    route_mismatches = 0
    row_count = 0
    details: dict[str, Any] = {}
    common_evidence = result["evidence_trace"]["0"]["evaluation"]
    score_counts = Counter(f"{row['kind']}:{row['reason']}" for row in common_evidence)
    for variant, spec in result["models"].items():
        base_variant = variant[:-3] if variant.endswith("_L2") else variant
        ledger_kind = "oracle" if base_variant.startswith("oracle") else (
            "retrospective" if base_variant.startswith("retrospective") else "prefix")
        trace_names = [base_variant]
        if variant.endswith("_L2"):
            trace_names.append(f"{ledger_kind}_L2")
        trace_names.append(ledger_kind)
        ledger_trace = next((result["ledger_trace"].get(name) for name in trace_names
                             if result["ledger_trace"].get(name) is not None), None)
        if ledger_trace is None:
            raise ValueError(f"no ledger trace for {variant}")
        evidence_key = "2" if variant.endswith("_L2") else "0"
        evidence_trace = result["evidence_trace"].get(evidence_key)
        if evidence_trace is None:
            raise ValueError(f"no evidence trace {evidence_key} for {variant}")
        features = {row["emission_index"]: row for row in ledger_trace["evaluation"]}
        evidences = {row["emission_index"]: row for row in evidence_trace["evaluation"]}
        variant_rows = expected_by_variant[variant]
        row_errors = []
        route_counts: dict[str, dict[str, int]] = {name: {} for name in ("M0", "M1", "M2", "M3")}
        for emission_index, saved in variant_rows.items():
            feature, evidence = features[emission_index], evidences[emission_index]
            # The frozen route contract requires a completed landmark.  A
            # uniform-end bracket may extend past issue, but its point estimate
            # must still satisfy the ledger's landmark_available flag.
            endpoint_available = feature.get("landmark_available") is True
            nodes = endpoint_nodes(feature, spec["endpoint_mode"], int(spec["nodes"])) \
                if endpoint_available else None
            duration_available = duration_nodes(feature, nodes) is not None
            for name in ("M0", "M1", "M2", "M3"):
                route = route_for(name, feature, endpoint_available, duration_available)
                route_counts[name][route] = route_counts[name].get(route, 0) + 1
                if route != saved[f"route_{name}"]:
                    route_mismatches += 1
                predicted = conditional_score(feature, evidence, spec, route)
                delta = abs(predicted - float(saved[name]))
                if delta > max_error:
                    max_error = delta
                if delta > 1.0e-9:
                    error_count += 1
                    if len(row_errors) < 5:
                        row_errors.append({"emission_index": emission_index, "model": name,
                                           "predicted": predicted, "saved": saved[name], "error": delta})
            row_count += 1
        gains = {
            "gain_M1_M0": mean(row["M1"] - row["M0"] for row in variant_rows.values()),
            "gain_M2_M0": mean(row["M2"] - row["M0"] for row in variant_rows.values()),
            "gain_M3_M2": mean(row["M3"] - row["M2"] for row in variant_rows.values()),
        }
        aggregate = result["results"][variant]
        gain_errors = {key: abs(value - aggregate[key]["estimate"]) for key, value in gains.items()}
        independent_intervals = {
            key: independent_cluster_interval(list(variant_rows.values()), key, result["stream_metadata"])
            for key in gains
        }
        interval_errors = {
            key: {field: abs(independent_intervals[key][field] - aggregate[key][field])
                  for field in ("estimate", "se", "lower", "upper")}
            for key in gains
        }
        diagnostics = result.get("duration_domain_diagnostics", {}).get(variant, {}).get("evaluation", {})
        badmark_saved = set(diagnostics.get("nonpositive_mark_emission_indices", []))
        badmark_saved.update(diagnostics.get("point_invalid_emission_indices", []))
        duration_bad_observed = set()
        duration_missing_observed = set()
        for emission_index, feature in features.items():
            if feature.get("landmark_available") is not True:
                continue
            nodes = endpoint_nodes(feature, spec["endpoint_mode"], int(spec["nodes"]))
            if duration_nodes(feature, nodes) is None:
                duration_bad_observed.add(emission_index)
            elif feature.get("onset_t") is None and feature.get("duration") is not None:
                duration_missing_observed.add(emission_index)
        details[variant] = {
            "rows": len(variant_rows),
            "max_error": max((item["error"] for item in row_errors), default=0.0),
            "sample_errors": row_errors,
            "route_counts": route_counts,
            "gains_from_scores": gains,
            "json_estimates": {key: aggregate[key]["estimate"] for key in gains},
            "gain_estimate_errors": gain_errors,
            "json_intervals": aggregate,
            "independent_intervals": independent_intervals,
            "interval_errors": interval_errors,
            "duration_domain_diagnostics": diagnostics,
            "observed_duration_badmark_ids": sorted(duration_bad_observed),
            "saved_badmark_ids": sorted(badmark_saved),
            "badmark_id_mismatch": sorted(duration_bad_observed ^ badmark_saved),
            "observed_positive_stored_duration_ids": sorted(duration_missing_observed),
        }
    return {
        "trial": str(path),
        "scores_source": str(scores_path),
        "scores_source_kind": scores_kind,
        "scores_sha256": hashlib.sha256(scores_path.read_bytes()).hexdigest(),
        "family": family,
        "case": case,
        "replicate": replicate,
        "score_rows": row_count,
        "max_abs_score_error": max_error,
        "score_error_count_gt_1e-9": error_count,
        "route_mismatch_count": route_mismatches,
        "details": details,
        "counts": result["counts"],
        "independent_evaluation_issued": len(common_evidence),
        "independent_evaluation_evidence": dict(sorted(score_counts.items())),
        "numerical_fixture": numerical_fixture_check(),
    }


def report_failures(report: dict[str, Any]) -> list[str]:
    failures = []
    if report["score_error_count_gt_1e-9"]:
        failures.append("score discrepancy exceeds 1e-9")
    if report["route_mismatch_count"]:
        failures.append("route mismatch")
    max_interval_error = max(
        max(error.values()) for detail in report["details"].values()
        for error in detail["interval_errors"].values()
    )
    if max_interval_error > 1.0e-9:
        failures.append("interval discrepancy exceeds 1e-9")
    if any(detail["badmark_id_mismatch"] for detail in report["details"].values()):
        failures.append("bad-mark diagnostic mismatch")
    if report["numerical_fixture"]["max_abs_error"] > 1.0e-10:
        failures.append("normal log-CDF fixture discrepancy exceeds 1e-10")
    report["max_interval_error"] = max_interval_error
    report["audit_failures"] = failures
    return failures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial", type=Path, required=True)
    parser.add_argument("--scores", type=Path, required=True)
    parser.add_argument("--scores-kind", default="growing-stream snapshot")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_trial(args.trial, args.scores, args.scores_kind)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    failures = report_failures(report)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: report[key] for key in ("trial", "score_rows", "max_abs_score_error",
                                                    "score_error_count_gt_1e-9", "route_mismatch_count",
                                                    "max_interval_error", "audit_failures")}))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
