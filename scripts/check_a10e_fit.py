#!/usr/bin/env python3
"""Independent audit of a completed A10e real-development payload.

The checker reads serialized models, ledgers, evidence, scores, summaries and
receipts only.  It does not read native acquisitions or import candidate fit
or profile implementations.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

ROOT = next(parent for parent in Path(__file__).resolve().parents
            if (parent / "configs/a10e_real_fit.json").exists())
sys.path.insert(0, str(ROOT / "scripts"))
from check_a10d_scores import (  # noqa: E402
    TOL,
    current_durations,
    conditional_score,
    endpoint_nodes,
    q_available,
    route_for,
)

VARIANTS = ("primary", "joint_placebo", "uniform_end", "q_only", "delay_2", "type_within")
DELAYS = {"delay_2": "2.0"}
GAIN_FIELDS = {
    "gain_M2_M0": ("M2", "M0"),
    "gain_M3_M2": ("M3", "M2"),
    "gain_M3_P3": ("M3", "P3"),
    "gain_P3_M2": ("P3", "M2"),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def beta_zero_map(spec: dict[str, Any]) -> dict[str, bool]:
    values = {}
    for name in ("M3", "P3"):
        coefficients = spec["models"][name].get("coefficients", {})
        additional = [float(coefficients[term]) for term in ("beta", "beta_type", "beta_within")
                      if term in coefficients]
        values[name] = bool(additional) and all(value == 0.0 for value in additional)
    return values


def expected_population(features: dict[int, dict[str, Any]], evidences: dict[int, dict[str, Any]],
                        spec: dict[str, Any]) -> tuple[set[int], dict[str, Counter[str]]]:
    expected: set[int] = set()
    routes = {name: Counter() for name in ("M0", "M2", "M3", "P3")}
    zeros = beta_zero_map(spec)
    for emission_index, feature in features.items():
        evidence = evidences.get(emission_index)
        if evidence is None or evidence.get("kind") == "excluded":
            continue
        nodes = endpoint_nodes(feature, spec["endpoint_mode"], int(spec["nodes"])) \
            if feature.get("landmark_available") is True else None
        endpoint = nodes is not None
        current_mark = current_durations(feature, nodes) is not None
        row_routes = {name: route_for(name, feature, endpoint, current_mark, zeros.get(name, False))
                      for name in routes}
        if spec.get("joint_marks") and not (endpoint and q_available(feature)
                                             and current_mark
                                             and feature.get("previous_duration") is not None
                                             and float(feature["previous_duration"]) > 0.0):
            continue
        expected.add(emission_index)
        for name, route in row_routes.items():
            routes[name][route] += 1
    return expected, routes


def audit_profile_directory(directory: Path, source: dict[str, Any], parameter_hash: str,
                            failures: list[dict[str, Any]]) -> dict[str, Any] | None:
    profile_dir = directory / "profiles"
    receipt_path = profile_dir / "receipt.json"
    if not profile_dir.exists():
        return None
    if not receipt_path.exists():
        failures.append({"kind": "profile_receipt_missing"})
        return {"present": True, "status": None}
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("status") != "completed":
        failures.append({"kind": "profile_not_completed", "status": receipt.get("status")})
    if receipt.get("source") != source:
        failures.append({"kind": "profile_source_mismatch"})
    if receipt.get("parameters_sha256") != parameter_hash:
        failures.append({"kind": "profile_parameter_hash_mismatch"})
    listed = receipt.get("files_sha256", {})
    for name, expected in listed.items():
        path = profile_dir / name
        if not path.exists() or digest(path) != expected:
            failures.append({"kind": "profile_file_hash_mismatch", "file": name})
    profile_counts = {}
    for variant in VARIANTS:
        path = profile_dir / f"{variant}.json"
        model_path = directory / f"{variant}-model.json"
        if not path.exists() or not model_path.exists():
            failures.append({"kind": "profile_variant_missing", "variant": variant})
            continue
        payload = json.loads(path.read_text())
        if payload.get("schema_version") != "a10d-fit-profile-v1":
            failures.append({"kind": "profile_schema", "variant": variant})
        if abs(float(payload.get("likelihood_ratio_cutoff", math.nan)) - 3.841) > TOL:
            failures.append({"kind": "profile_cutoff", "variant": variant})
        if abs(float(payload.get("support_delta_negative_log_likelihood", math.nan)) - 1.9205) > TOL:
            failures.append({"kind": "profile_support_delta", "variant": variant})
        model_names = set(json.loads(model_path.read_text()).get("models", {})) | {"R0"}
        if set(payload.get("models", {})) != model_names:
            failures.append({"kind": "profile_model_inventory", "variant": variant})
        count = 0
        for model_name, model_profile in payload.get("models", {}).items():
            frozen_objective = model_profile.get("frozen_objective")
            if not finite(frozen_objective):
                failures.append({"kind": "profile_frozen_objective", "variant": variant, "model": model_name})
                continue
            for parameter, profile in model_profile.get("profiles", {}).items():
                count += 1
                evaluations = profile.get("evaluations", [])
                support = profile.get("likelihood_support_interval", {})
                bounds = profile.get("working_bounds", [])
                if profile.get("status") != "profiled" or len(bounds) != 2:
                    failures.append({"kind": "profile_status_or_bounds", "variant": variant,
                                     "model": model_name, "parameter": parameter})
                if not (finite(profile.get("estimate")) and finite(support.get("lower"))
                        and finite(support.get("upper")) and len(bounds) == 2
                        and finite(bounds[0]) and finite(bounds[1])):
                    failures.append({"kind": "profile_nonfinite_support", "variant": variant,
                                     "model": model_name, "parameter": parameter})
                    continue
                if support["lower"] > support["upper"] or not support["lower"] <= profile["estimate"] <= support["upper"]:
                    failures.append({"kind": "profile_support_order", "variant": variant,
                                     "model": model_name, "parameter": parameter})
                if bool(support.get("lower_clipped_to_bound")) != (abs(support["lower"] - bounds[0]) <= 1.0e-7):
                    failures.append({"kind": "profile_lower_boundary_flag", "variant": variant,
                                     "model": model_name, "parameter": parameter})
                if bool(support.get("upper_clipped_to_bound")) != (abs(support["upper"] - bounds[1]) <= 1.0e-7):
                    failures.append({"kind": "profile_upper_boundary_flag", "variant": variant,
                                     "model": model_name, "parameter": parameter})
                zero_seen = False
                for evaluation in evaluations:
                    objective = evaluation.get("objective")
                    likelihood_ratio = evaluation.get("likelihood_ratio")
                    raw_ratio = evaluation.get("raw_likelihood_ratio")
                    if not all(finite(value) for value in (objective, likelihood_ratio, raw_ratio, evaluation.get("value"))):
                        failures.append({"kind": "profile_nonfinite_evaluation", "variant": variant,
                                         "model": model_name, "parameter": parameter})
                        continue
                    calculated_ratio = 2.0 * (float(objective) - float(frozen_objective))
                    if abs(float(likelihood_ratio) - calculated_ratio) > 1.0e-7 or abs(float(raw_ratio) - float(likelihood_ratio)) > 1.0e-7:
                        failures.append({"kind": "profile_likelihood_ratio", "variant": variant,
                                         "model": model_name, "parameter": parameter})
                    if abs(float(likelihood_ratio)) <= 1.0e-6:
                        zero_seen = True
                if not zero_seen:
                    failures.append({"kind": "profile_no_frozen_evaluation", "variant": variant,
                                     "model": model_name, "parameter": parameter})
        profile_counts[variant] = count
    return {"present": True, "status": receipt.get("status"), "files": sorted(listed),
            "profile_parameter_counts": profile_counts}


def audit(directory: Path) -> dict[str, Any]:
    directory = Path(directory)
    failures: list[dict[str, Any]] = []
    receipt_path = directory / "receipt.json"
    config = json.loads((ROOT / "configs/a10e_real_fit.json").read_text())
    if not receipt_path.exists():
        return {"directory": str(directory), "audit_failures": [{"kind": "receipt_missing"}]}
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("status") != "fit_completed":
        failures.append({"kind": "fit_not_completed", "status": receipt.get("status")})
    if receipt.get("scope") != config["scope"] or receipt.get("gate_choice") != config["gate_choice"]:
        failures.append({"kind": "receipt_scope_or_gate_mismatch"})
    listed = receipt.get("files_sha256", {})
    for name, expected in listed.items():
        path = directory / name
        if not path.exists() or digest(path) != expected:
            failures.append({"kind": "payload_hash_mismatch", "file": name})
    frozen_path = directory / "frozen_parameters.json"
    if not frozen_path.exists() or receipt.get("parameters_sha256") != digest(frozen_path):
        failures.append({"kind": "parameter_hash_mismatch"})
    frozen = json.loads(frozen_path.read_text()) if frozen_path.exists() else {}
    for name in VARIANTS:
        model_path = directory / f"{name}-model.json"
        if not model_path.exists():
            failures.append({"kind": "model_missing", "variant": name})
        elif name in frozen and json.loads(model_path.read_text()) != frozen[name]:
            failures.append({"kind": "frozen_model_mismatch", "variant": name})
    native = receipt.get("native", {})
    source_hashes = native.get("source_sha256", {})
    if len(source_hashes) != int(config["expected_acquisitions"]):
        failures.append({"kind": "native_acquisition_count", "expected": config["expected_acquisitions"],
                         "observed": len(source_hashes)})
    if not finite(native.get("native_rows")) or int(native.get("native_rows", 0)) <= 0:
        failures.append({"kind": "native_row_count_invalid"})
    if not finite(native.get("duplicate_rows_removed")) or int(native.get("duplicate_rows_removed", -1)) < 0:
        failures.append({"kind": "native_duplicate_count_invalid"})

    traces: dict[str, tuple[dict[int, dict[str, Any]], dict[int, dict[str, Any]]]] = {}
    for delay in ("0.0", "2.0"):
        ledger_path, evidence_path = directory / f"ledger-{delay}.json", directory / f"evidence-{delay}.json"
        if not ledger_path.exists() or not evidence_path.exists():
            failures.append({"kind": "trace_missing", "delay": delay})
            continue
        ledger = json.loads(ledger_path.read_text())
        evidence = json.loads(evidence_path.read_text())
        features = {int(row["emission_index"]): row for row in ledger}
        evidences = {int(row["emission_index"]): row for row in evidence}
        traces[delay] = (features, evidences)
        if set(features) != set(evidences):
            failures.append({"kind": "trace_id_mismatch", "delay": delay})
        for row in ledger:
            issue = float(row["issue_time"])
            if not config["start_jd"] <= issue < config["stop_jd"]:
                failures.append({"kind": "issue_window", "delay": delay, "emission_index": row["emission_index"]})
            if float(row["prefix_last_jd"]) > float(row["emitted_at"]):
                failures.append({"kind": "prefix_future_leak", "delay": delay, "emission_index": row["emission_index"]})
        for row in evidence:
            if float(row["computed_as_of"]) > config["stop_jd"]:
                failures.append({"kind": "evidence_future_leak", "delay": delay, "emission_index": row["emission_index"]})

    variant_reports: dict[str, Any] = {}
    for name in VARIANTS:
        score_path = directory / f"{name}-scores.json"
        model_path = directory / f"{name}-model.json"
        summary_path = directory / "summary.json"
        if not score_path.exists() or not model_path.exists() or not summary_path.exists():
            failures.append({"kind": "variant_payload_missing", "variant": name})
            continue
        spec = json.loads(model_path.read_text())
        summary_all = json.loads(summary_path.read_text())
        summary = summary_all.get(name)
        delay_key = DELAYS.get(name, "0.0")
        if delay_key not in traces:
            continue
        features, evidences = traces[delay_key]
        rows = json.loads(score_path.read_text())
        expected, expected_routes = expected_population(features, evidences, spec)
        ids = [int(row["emission_index"]) for row in rows]
        if len(ids) != len(set(ids)):
            failures.append({"kind": "score_id_duplicate", "variant": name})
        if set(ids) != expected:
            failures.append({"kind": "score_population", "variant": name,
                             "expected": len(expected), "saved": len(ids),
                             "missing": sorted(expected - set(ids))[:5],
                             "extra": sorted(set(ids) - expected)[:5]})
        feature_rows = {int(k): v for k, v in features.items()}
        evidence_rows = {int(k): v for k, v in evidences.items()}
        max_error = 0.0
        gain_errors = 0
        route_errors = 0
        likelihoods = Counter()
        actual_routes = {model: Counter() for model in ("M0", "M2", "M3", "P3")}
        for row in rows:
            index = int(row["emission_index"])
            feature, evidence = feature_rows[index], evidence_rows[index]
            nodes = endpoint_nodes(feature, spec["endpoint_mode"], int(spec["nodes"])) \
                if feature.get("landmark_available") is True else None
            endpoint, current_mark = nodes is not None, current_durations(feature, nodes) is not None
            zeros = beta_zero_map(spec)
            routes = {model: route_for(model, feature, endpoint, current_mark, zeros.get(model, False))
                      for model in ("M0", "M2", "M3", "P3")}
            for model, route in routes.items():
                actual_routes[model][route] += 1
                if row.get(f"{model}_route") != route:
                    route_errors += 1
                predicted = conditional_score(feature, evidence, spec, route)
                if not finite(row.get(model)):
                    failures.append({"kind": "nonfinite_score", "variant": name, "emission_index": index, "model": model})
                else:
                    max_error = max(max_error, abs(predicted - float(row[model])))
            for field, (left, right) in GAIN_FIELDS.items():
                if field not in row:
                    continue
                if not finite(row.get(field)) or abs(float(row[field]) - (float(row[left]) - float(row[right]))) > TOL:
                    gain_errors += 1
            for model in ("M0", "M2", "M3", "P3"):
                likelihoods[model] += float(row[model])
        if max_error > TOL:
            failures.append({"kind": "score_discrepancy", "variant": name, "max_error": max_error})
        if route_errors:
            failures.append({"kind": "route_discrepancy", "variant": name, "count": route_errors})
        if gain_errors:
            failures.append({"kind": "gain_identity", "variant": name, "count": gain_errors})
        if summary is not None:
            for model, total in likelihoods.items():
                saved = summary.get("log_likelihood", {}).get(model)
                if saved is None or abs(float(saved) - total) > TOL:
                    failures.append({"kind": "likelihood_total", "variant": name, "model": model,
                                     "saved": saved, "calculated": total})
            if summary.get("routes") != {model: dict(counts) for model, counts in actual_routes.items()}:
                failures.append({"kind": "route_summary", "variant": name})
            means = {
                "M3_M2": sum(float(row["M3"]) - float(row["M2"]) for row in rows) / len(rows),
                "P3_M2": sum(float(row["P3"]) - float(row["M2"]) for row in rows) / len(rows),
                "M3_P3": sum(float(row["M3"]) - float(row["P3"]) for row in rows) / len(rows),
                "M2_M0": sum(float(row["M2"]) - float(row["M0"]) for row in rows) / len(rows),
            }
            for field, calculated in means.items():
                saved = summary.get("mean_in_sample_gain", {}).get(field)
                if saved is None or abs(float(saved) - calculated) > TOL:
                    failures.append({"kind": "gain_summary", "variant": name, "field": field,
                                     "saved": saved, "calculated": calculated})
        variant_reports[name] = {"rows": len(rows), "expected_rows": len(expected),
                                 "max_abs_score_error": max_error, "route_errors": route_errors,
                                 "gain_errors": gain_errors, "routes": {m: dict(c) for m, c in actual_routes.items()},
                                 "beta_zero": beta_zero_map(spec)}

    profile_report = audit_profile_directory(directory, receipt.get("source"), receipt.get("parameters_sha256"), failures)
    return {"directory": str(directory), "status": receipt.get("status"), "variant_reports": variant_reports,
            "profile_report": profile_report, "audit_failures": failures,
            "input_sha256": {name: digest(directory / name) for name in listed if (directory / name).exists()}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = audit(args.directory)
    except Exception as exc:
        report = {"directory": str(args.directory), "audit_failures": [{"kind": "fatal", "error": str(exc)}]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"status": report.get("status"), "audit_failures": len(report.get("audit_failures", [])),
                      "variants": report.get("variant_reports", {})}))
    if report.get("audit_failures"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
