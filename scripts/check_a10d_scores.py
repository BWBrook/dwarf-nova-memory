#!/usr/bin/env python3
"""Independent reconciliation of serialized A10d directional scores.

This checker reads only the completed trial, its score stream, and the
serialized ledger/evidence/model metadata.  It deliberately does not import
the candidate forecast implementation.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from typing import Any


SQRT2 = math.sqrt(2.0)
LOG_SQRT_2PI = 0.5 * math.log(2.0 * math.pi)
EPS = 1.0e-12
TOL = 1.0e-9
VARIANTS = ("primary", "joint_placebo", "uniform_end", "q_only", "delay_2", "type_within")


def log_ndtr(x: float) -> float:
    if -32.0 <= x <= 0.0:
        return math.log(0.5 * math.erfc(-x / SQRT2))
    if x < -32.0:
        inv = 1.0 / (x * x)
        series = (1.0 - inv + 3.0 * inv**2 - 15.0 * inv**3
                  + 105.0 * inv**4 - 945.0 * inv**5 + 10395.0 * inv**6
                  - 135135.0 * inv**7)
        return (-0.5 * x * x - math.log(-x) - LOG_SQRT_2PI
                + math.log(series))
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
    if endpoint_mode == "point":
        end = feature.get("end_t")
        return None if end is None else [float(end)]
    lo, hi = feature.get("end_lo"), feature.get("end_hi")
    if lo is None or hi is None:
        return None
    lo, hi = float(lo), min(float(hi), float(feature["issue_time"]))
    if hi < lo - EPS:
        return None
    if hi - lo <= EPS or nodes == 1:
        return [lo]
    return [lo + (hi - lo) * i / (nodes - 1) for i in range(nodes)]


def current_durations(feature: dict[str, Any], nodes: list[float] | None) -> list[float] | None:
    if nodes is None:
        return None
    onset = feature.get("onset_t")
    if onset is None:
        return None
    durations = [node - float(onset) for node in nodes]
    return durations if all(duration > 0.0 for duration in durations) else None


def q_available(feature: dict[str, Any]) -> bool:
    value = feature.get("previous_gap")
    return feature.get("previous_gap_covered") is True and value is not None and float(value) > 0.0


def previous_duration_available(feature: dict[str, Any]) -> bool:
    value = feature.get("previous_duration")
    return value is not None and float(value) > 0.0


def route_for(model_name: str, feature: dict[str, Any], endpoint: bool,
              current_mark: bool, beta_zero: bool = False) -> str:
    if not endpoint:
        return "R0"
    if not q_available(feature):
        return "M0"
    if model_name == "M0":
        return "M0"
    if model_name == "M2":
        return "M2"
    if model_name == "M3":
        if beta_zero:
            return "M2"
        return "M3" if current_mark else "M2"
    if model_name == "P3":
        return "P3" if previous_duration_available(feature) else "M2"
    raise ValueError(f"unknown route model {model_name}")


def model_value(model: dict[str, Any], feature: dict[str, Any], endpoint: float | None,
                current_duration: float | None) -> float:
    values: dict[str, float] = {}
    centers = model.get("centers", {})
    scales = model.get("scales", {})
    terms = model.get("terms", [])
    if "previous_gap" in terms:
        previous = feature.get("previous_gap")
        if not q_available(feature):
            raise ValueError("previous-gap model term lacks q")
        values["previous_gap"] = (math.log(float(previous)) - float(centers["previous_gap"])) / float(scales["previous_gap"])
    if "earlier_level" in terms:
        earlier = feature.get("earlier_gaps") or []
        # The serialized gaps are already log gaps.  Missing L is represented
        # by the training center, hence zero after centering.
        level = sum(float(x) for x in earlier) / len(earlier) if earlier else float(centers["earlier_level"])
        values["earlier_level"] = (level - float(centers["earlier_level"])) / float(scales["earlier_level"])
    mark_term = any(term in terms for term in ("beta", "beta_type", "beta_within"))
    if mark_term:
        mark_kind = model.get("metadata", {}).get("mark_kind", "current")
        if mark_kind == "previous":
            mark_duration = feature.get("previous_duration")
        else:
            if endpoint is None:
                raise ValueError("current mark term lacks endpoint")
            mark_duration = current_duration
        if mark_duration is None or float(mark_duration) <= 0.0:
            raise ValueError("mark term lacks positive duration")
        mark_duration = float(mark_duration)
        mode = model.get("metadata", {}).get("mark_mode", "log_duration")
        if mode == "log_duration":
            values["beta"] = (math.log(mark_duration) - float(centers["mark"])) / float(scales["mark"])
        elif mode == "type_within":
            duration_type = int(mark_duration >= 12.0)
            type_centers = centers["mark_type"]
            values["beta_type"] = float(duration_type)
            values["beta_within"] = (math.log(mark_duration) - float(type_centers[str(duration_type)])) / float(scales["mark_within"])
        else:
            raise ValueError(f"unsupported mark mode {mode}")
    mu = float(model["intercept"])
    coefficients = model.get("coefficients", {})
    for term, coefficient in coefficients.items():
        if term == "beta" and "beta" not in values:
            continue
        if term in ("beta_type", "beta_within") and term not in values:
            continue
        if term not in values:
            raise ValueError(f"missing serialized feature value for {term}")
        mu += float(coefficient) * values[term]
    return mu


def conditional_score(feature: dict[str, Any], evidence: dict[str, Any],
                      spec: dict[str, Any], route: str) -> float:
    issue = float(feature["issue_time"])
    if route == "R0":
        model = spec["r0"]
        nodes: list[float | None] = [None]
    else:
        model = spec["models"][route]
        nodes = endpoint_nodes(feature, spec["endpoint_mode"], int(spec["nodes"])) or []
        if not nodes:
            raise ValueError(f"{route} selected without endpoint")
    numerators: list[float] = []
    denominators: list[float] = []
    durations = current_durations(feature, [node for node in nodes if node is not None])
    for index, endpoint in enumerate(nodes):
        age = 0.0 if endpoint is None else issue - float(endpoint)
        if age < -EPS:
            raise ValueError("endpoint follows issue")
        duration = None if endpoint is None else (durations[index] if durations is not None else None)
        mu = model_value(model, feature, endpoint, duration)
        sigma = float(model["sigma"])
        anchor = issue if endpoint is None else float(endpoint)
        if evidence["kind"] == "interval":
            lower = max(float(evidence["onset_lo"]), issue) - anchor
            upper = float(evidence["onset_hi"]) - anchor
            numerators.append(logdiffexp(lognormal_cdf(upper, mu, sigma),
                                         lognormal_cdf(lower, mu, sigma)))
        elif evidence["kind"] == "right_censored":
            censor = float(evidence["censor_at"]) - anchor
            numerators.append(lognormal_sf(censor, mu, sigma))
        else:
            raise ValueError(f"unsupported evidence kind {evidence['kind']}")
        denominators.append(lognormal_sf(age, mu, sigma))
    # A bracket is a marginal likelihood ratio: do not average conditional
    # ratios node by node.
    return (numerators[0] - denominators[0] if len(numerators) == 1
            else logsumexp(numerators) - logsumexp(denominators))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_trial(trial_path: Path, scores_path: Path) -> dict[str, Any]:
    payload = json.loads(trial_path.read_text())
    if payload.get("success") is not True:
        raise ValueError(f"trial is not complete: {trial_path}")
    result = payload["result"]
    family, case, replicate = result["family"], result["case"], result["replicate"]
    raw_scores = [json.loads(line) for line in scores_path.read_text().splitlines() if line.strip()]
    scores = [row for row in raw_scores if row.get("family") == family and row.get("case") == case
              and row.get("replicate") == replicate]
    by_variant = {variant: {row["emission_index"]: row for row in scores if row["variant"] == variant}
                  for variant in VARIANTS}
    errors: list[dict[str, Any]] = []
    route_mismatches = 0
    score_rows = 0
    max_score_error = 0.0
    details: dict[str, Any] = {}
    ledger_cache: dict[str, dict[int, dict[str, Any]]] = {}
    evidence_cache: dict[str, dict[int, dict[str, Any]]] = {}
    for key in ("0.0", "2.0"):
        ledger_cache[key] = {row["emission_index"]: row for row in result["audit_trace"]["ledger"][key]["evaluation"]}
        evidence_cache[key] = {row["emission_index"]: row for row in result["audit_trace"]["evidence"][key]["evaluation"]}

    for variant in VARIANTS:
        spec = result["models"].get(variant)
        if spec is None:
            errors.append({"kind": "missing_variant", "variant": variant})
            continue
        key = "2.0" if variant == "delay_2" else "0.0"
        features, evidences = ledger_cache[key], evidence_cache[key]
        expected_ids: set[int] = set()
        route_counts: dict[str, Counter[str]] = {name: Counter() for name in ("M0", "M2", "M3", "P3")}
        for emission_index, feature in features.items():
            endpoint_nodes_value = endpoint_nodes(feature, spec["endpoint_mode"], int(spec["nodes"])) \
                if feature.get("landmark_available") is True else None
            endpoint = endpoint_nodes_value is not None
            current_mark = current_durations(feature, endpoint_nodes_value) is not None
            beta_model = spec["models"]["M3"].get("coefficients", {})
            beta_zero = all(abs(float(beta_model.get(term, 0.0))) <= TOL
                            for term in ("beta", "beta_type", "beta_within"))
            routes = {name: route_for(name, feature, endpoint, current_mark, beta_zero)
                      for name in ("M0", "M2", "M3", "P3")}
            # The placebo is scored only on the joint-valid mark population.
            if spec.get("joint_marks") and not (endpoint and q_available(feature)
                                                 and current_mark and previous_duration_available(feature)):
                continue
            expected_ids.add(emission_index)
            for name, route in routes.items():
                route_counts[name][route] += 1
        saved = by_variant[variant]
        if set(saved) != expected_ids:
            missing, extra = sorted(expected_ids - set(saved)), sorted(set(saved) - expected_ids)
            errors.append({"kind": "scored_population", "variant": variant,
                           "expected": len(expected_ids), "saved": len(saved),
                           "missing_sample": missing[:5], "extra_sample": extra[:5]})
        variant_max = 0.0
        variant_error_count = 0
        gain_errors = 0
        nesting_errors = 0
        row_errors: list[dict[str, Any]] = []
        for emission_index, row in saved.items():
            if emission_index not in features or emission_index not in evidences:
                errors.append({"kind": "missing_trace", "variant": variant, "emission_index": emission_index})
                continue
            feature, evidence = features[emission_index], evidences[emission_index]
            endpoint_nodes_value = endpoint_nodes(feature, spec["endpoint_mode"], int(spec["nodes"])) \
                if feature.get("landmark_available") is True else None
            endpoint = endpoint_nodes_value is not None
            current_mark = current_durations(feature, endpoint_nodes_value) is not None
            beta_model = spec["models"]["M3"].get("coefficients", {})
            beta_zero = all(abs(float(beta_model.get(term, 0.0))) <= TOL
                            for term in ("beta", "beta_type", "beta_within"))
            routes = {name: route_for(name, feature, endpoint, current_mark, beta_zero)
                      for name in ("M0", "M2", "M3", "P3")}
            for name, route in routes.items():
                if row.get(f"{name}_route") != route:
                    route_mismatches += 1
                    if len(row_errors) < 5:
                        row_errors.append({"kind": "route", "emission_index": emission_index,
                                           "model": name, "saved": row.get(f"{name}_route"), "expected": route})
                predicted = conditional_score(feature, evidence, spec, route)
                delta = abs(predicted - float(row[name]))
                max_score_error = max(max_score_error, delta)
                variant_max = max(variant_max, delta)
                if delta > TOL:
                    variant_error_count += 1
                    if len(row_errors) < 5:
                        row_errors.append({"kind": "score", "emission_index": emission_index,
                                           "model": name, "predicted": predicted,
                                           "saved": row[name], "error": delta})
            for field, lhs, rhs in (("gain_M2_M0", "M2", "M0"),
                                    ("gain_M3_M2", "M3", "M2"),
                                    ("gain_M3_P3", "M3", "P3"),
                                    ("gain_P3_M2", "P3", "M2")):
                delta = abs(float(row[field]) - (float(row[lhs]) - float(row[rhs])))
                if delta > TOL:
                    gain_errors += 1
            if routes["M2"] == "M0" and abs(float(row["M3"]) - float(row["M2"])) > TOL:
                nesting_errors += 1
            model_m3 = spec["models"]["M3"]
            beta_values = [float(model_m3["coefficients"].get(term, 0.0))
                           for term in ("beta", "beta_type", "beta_within")]
            if all(abs(beta) <= TOL for beta in beta_values) and routes["M3"] in ("M2", "M3"):
                if abs(float(row["M3"]) - float(row["M2"])) > TOL:
                    nesting_errors += 1
        score_rows += len(saved)
        if gain_errors:
            errors.append({"kind": "gain_identity", "variant": variant, "count": gain_errors})
        if nesting_errors:
            errors.append({"kind": "exact_nesting", "variant": variant, "count": nesting_errors})
        # The persisted interval estimates must equal the score-stream means.
        aggregate_errors = 0
        if saved:
            gains = {
                "gain_M2_M0": sum(float(r["M2"]) - float(r["M0"]) for r in saved.values()) / len(saved),
                "gain_M3_M2": sum(float(r["M3"]) - float(r["M2"]) for r in saved.values()) / len(saved),
                "gain_M3_P3": sum(float(r["M3"]) - float(r["P3"]) for r in saved.values()) / len(saved),
                "gain_P3_M2": sum(float(r["P3"]) - float(r["M2"]) for r in saved.values()) / len(saved),
            }
            for years in ("3", "6"):
                for gain, estimate in gains.items():
                    persisted = result.get("intervals", {}).get(variant, {}).get(years, {}).get(gain, {}).get("estimate")
                    if persisted is not None and abs(float(persisted) - estimate) > TOL:
                        aggregate_errors += 1
        if aggregate_errors:
            errors.append({"kind": "aggregate_estimate", "variant": variant, "count": aggregate_errors})
        details[variant] = {
            "rows": len(saved),
            "expected_rows": len(expected_ids),
            "route_counts": {name: dict(counts) for name, counts in route_counts.items()},
            "max_abs_score_error": variant_max,
            "score_error_count_gt_1e-9": variant_error_count,
            "row_error_examples": row_errors,
            "gain_identity_error_count": gain_errors,
            "exact_nesting_error_count": nesting_errors,
            "aggregate_estimate_error_count": aggregate_errors,
        }

    # Delay mapping is a serialized trace contract: same emission IDs and a
    # two-day issue-time shift, while score population remains unchanged.
    delay_errors = 0
    primary_features = ledger_cache["0.0"]
    delay_features = ledger_cache["2.0"]
    for emission_index in set(primary_features) & set(delay_features):
        delta = float(delay_features[emission_index]["issue_time"]) - float(primary_features[emission_index]["issue_time"])
        if abs(delta - 2.0) > TOL:
            delay_errors += 1
    # A delayed issuance can legitimately lose the final boundary row; it may
    # not introduce a row absent from the zero-delay trace.
    if not set(delay_features).issubset(primary_features) or delay_errors:
        errors.append({"kind": "delay_mapping", "primary_rows": len(primary_features),
                       "delay_rows": len(delay_features), "issue_shift_errors": delay_errors})

    report = {
        "checker": "check_a10d_scores",
        "trial": str(trial_path),
        "scores": str(scores_path),
        "input_sha256": {"trial": digest(trial_path), "scores": digest(scores_path)},
        "family": family,
        "case": case,
        "replicate": replicate,
        "score_rows": score_rows,
        "max_abs_score_error": max_score_error,
        "route_mismatch_count": route_mismatches,
        "delay_mapping_issue_shift_errors": delay_errors,
        "details": details,
        "audit_failures": errors,
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial", type=Path, required=True)
    parser.add_argument("--scores", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = check_trial(args.trial, args.scores)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: report[key] for key in
                      ("case", "score_rows", "max_abs_score_error", "route_mismatch_count",
                       "delay_mapping_issue_shift_errors", "audit_failures")}))
    if report["audit_failures"] or report["max_abs_score_error"] > TOL or report["route_mismatch_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
