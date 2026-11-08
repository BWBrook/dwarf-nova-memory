#!/usr/bin/env python3
"""Independent checker for the sealed A10f evaluation artifact.

The checker consumes only the serialized ledgers, evidence, frozen models and
score streams.  In particular, it does not import the forecast, prefix,
directional or evaluation-runner implementations.  Failures are accumulated
so that a damaged artifact is diagnosed in one pass.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
from typing import Any

try:  # Package import for tests; sibling import for direct CLI execution.
    from scripts.check_a10d_scores import (
        conditional_score, current_durations, endpoint_nodes,
        previous_duration_available, q_available,
    )
except ModuleNotFoundError:  # pragma: no cover - exercised by the CLI
    from check_a10d_scores import (
        conditional_score, current_durations, endpoint_nodes,
        previous_duration_available, q_available,
    )


VARIANTS = ("primary", "joint_placebo", "uniform_end", "q_only", "delay_2", "type_within")
MODELS = ("M0", "M2", "M3", "P3")
START = 2436934.5
END = 2458119.5
TRAINING_CUTOFF = 2436934.5
YEARS = 6
TOL = 1.0e-9
REFERENCE_GAIN = 0.004519560867443926
FROZEN_SHA256 = "ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def concordance_digest(ledger: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> str:
    """Canonical digest used by the independent candidate/reference check."""
    payload = json.dumps([ledger, evidence], sort_keys=True, allow_nan=False,
                         separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def close(left: Any, right: Any, tolerance: float = TOL) -> bool:
    try:
        return abs(float(left) - float(right)) <= tolerance
    except (TypeError, ValueError):
        return left == right


# This is deliberately local to the checker.  It is the standard-library-only
# inverse used for the one-sided 95% lower bound in the preregistered test.
def _beta_continued_fraction(a: float, b: float, x: float) -> float:
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


def _regularized_beta(x: float, a: float, b: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                     + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _beta_continued_fraction(a, b, x) / a
    return 1.0 - front * _beta_continued_fraction(b, a, 1.0 - x) / b


def _student_t_cdf(value: float, degrees: float) -> float:
    if value == 0.0:
        return 0.5
    x = degrees / (degrees + value * value)
    tail = 0.5 * _regularized_beta(x, degrees / 2.0, 0.5)
    return 1.0 - tail if value > 0.0 else tail


def student_t_ppf(probability: float, degrees: float) -> float:
    if not 0.0 < probability < 1.0 or degrees <= 0.0:
        raise ValueError("invalid Student-t quantile request")
    sign = 1.0 if probability >= 0.5 else -1.0
    target = probability if sign > 0 else 1.0 - probability
    lo, hi = 0.0, 1.0
    while _student_t_cdf(hi, degrees) < target:
        hi *= 2.0
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if _student_t_cdf(mid, degrees) < target:
            lo = mid
        else:
            hi = mid
    return sign * (lo + hi) / 2.0


def _zero_mark(model: dict[str, Any]) -> bool:
    coefficients = model.get("coefficients", {})
    values = [float(coefficients[name]) for name in ("beta", "beta_type", "beta_within")
              if name in coefficients]
    return bool(values) and all(value == 0.0 for value in values)


def route_for(model_name: str, model: dict[str, Any], feature: dict[str, Any],
              endpoint: bool, current_mark: bool) -> str:
    """Route with an explicit exact-zero offset identity."""
    if not endpoint:
        return "R0"
    if not q_available(feature):
        return "M0"
    if model_name in ("M0", "M2"):
        return model_name
    if _zero_mark(model):
        return "M2"
    if model_name == "M3":
        return "M3" if current_mark else "M2"
    if model_name == "P3":
        return "P3" if previous_duration_available(feature) else "M2"
    raise ValueError(f"unknown route model {model_name}")


def _read_json(path: Path, failures: list[dict[str, Any]], kind: str) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        failures.append({"kind": kind, "file": path.name, "error": str(exc)})
        return None


def _rows(path: Path, failures: list[dict[str, Any]], kind: str) -> list[dict[str, Any]]:
    value = _read_json(path, failures, kind)
    if not isinstance(value, list):
        failures.append({"kind": f"{kind}_not_list", "file": path.name})
        return []
    rows = []
    for index, row in enumerate(value):
        if not isinstance(row, dict):
            failures.append({"kind": f"{kind}_row_not_object", "file": path.name, "index": index})
            continue
        rows.append(row)
    return rows


def _check_time_inputs(ledgers: dict[str, list[dict[str, Any]]],
                       evidence: dict[str, list[dict[str, Any]]],
                       failures: list[dict[str, Any]]) -> None:
    for delay, rows in ledgers.items():
        for index, row in enumerate(rows):
            issue = row.get("issue_time")
            if not finite(issue) or not START <= float(issue) < END:
                failures.append({"kind": "issuance_range", "delay": delay, "index": index,
                                 "issue_time": issue})
            emitted = row.get("emitted_at")
            prefix = row.get("prefix_last_jd")
            if not finite(emitted) or not finite(prefix) or float(prefix) > float(emitted) + TOL:
                failures.append({"kind": "prefix_after_emission", "delay": delay,
                                 "emission_index": row.get("emission_index"),
                                 "prefix_last_jd": prefix, "emitted_at": emitted})
        for index, row in enumerate(evidence.get(delay, [])):
            asof = row.get("computed_as_of")
            if not finite(asof) or abs(float(asof) - END) > TOL:
                failures.append({"kind": "evidence_asof_cutoff", "delay": delay, "index": index,
                                 "computed_as_of": asof, "expected": END})


def primary_interval(rows: list[dict[str, Any]], origin: float = START,
                     years: int = YEARS) -> dict[str, Any]:
    if not rows:
        raise ValueError("no primary score rows")
    width = years * 365.25
    grouped: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        index = math.floor((float(row["issue_time"]) - origin) / width)
        grouped[index].append(float(row["M3"]) - float(row["M2"]))
    if len(grouped) < 2:
        raise ValueError("at least two nonempty calendar groups are required")
    counts = [len(grouped[index]) for index in sorted(grouped)]
    means = [sum(grouped[index]) / len(grouped[index]) for index in sorted(grouped)]
    total = sum(counts)
    estimate = sum(value for group in grouped.values() for value in group) / total
    blocks = len(means)
    se = math.sqrt(blocks * sum((count * (mean - estimate)) ** 2
                                for count, mean in zip(counts, means))
                   / (total * total * (blocks - 1)))
    critical = student_t_ppf(0.95, blocks - 1)
    lower, upper = estimate - critical * se, estimate + critical * se
    return {"estimate": estimate, "se": se, "lower": lower, "upper": upper,
            "confirmed": lower > 0.0, "n": total, "blocks": blocks,
            "origin": origin, "years": years,
            "interval": "one-sided 95% lower bound / two-sided 90% interval",
            "reference_gain": REFERENCE_GAIN,
            "upper_below_reference": upper < REFERENCE_GAIN,
            "cluster_counts": counts}


def _compare_primary(saved: Any, calculated: dict[str, Any], failures: list[dict[str, Any]]) -> None:
    if not isinstance(saved, dict):
        failures.append({"kind": "primary_not_object"})
        return
    for field in ("estimate", "se", "lower", "upper", "confirmed", "n", "blocks", "origin", "years",
                  "interval", "reference_gain", "upper_below_reference"):
        if field not in saved:
            failures.append({"kind": "primary_missing_field", "field": field})
        elif field == "confirmed":
            if bool(saved[field]) != bool(calculated[field]):
                failures.append({"kind": "primary_mismatch", "field": field,
                                 "saved": saved[field], "calculated": calculated[field]})
        elif field in ("n", "blocks", "years"):
            try:
                if int(saved[field]) != int(calculated[field]):
                    raise ValueError
            except (TypeError, ValueError):
                failures.append({"kind": "primary_mismatch", "field": field,
                                 "saved": saved[field], "calculated": calculated[field]})
        elif field == "interval":
            if saved[field] != calculated[field]:
                failures.append({"kind": "primary_mismatch", "field": field,
                                 "saved": saved[field], "calculated": calculated[field]})
        elif field == "upper_below_reference":
            if bool(saved[field]) != bool(calculated[field]):
                failures.append({"kind": "primary_mismatch", "field": field,
                                 "saved": saved[field], "calculated": calculated[field]})
        elif field == "reference_gain":
            try:
                valid = float(saved[field]) == REFERENCE_GAIN
            except (TypeError, ValueError):
                valid = False
            if not valid:
                failures.append({"kind": "primary_mismatch", "field": field,
                                 "saved": saved[field], "calculated": REFERENCE_GAIN})
        elif not close(saved[field], calculated[field]):
            failures.append({"kind": "primary_mismatch", "field": field,
                             "saved": saved[field], "calculated": calculated[field]})


def audit(directory: Path) -> dict[str, Any]:
    directory = Path(directory)
    failures: list[dict[str, Any]] = []
    required = {"receipt.json", "concordance.json", "frozen_parameters.json", "ledger-0.0.json", "ledger-2.0.json",
                "evidence-0.0.json", "evidence-2.0.json", "primary.json"}
    required.update(f"{variant}-scores.json" for variant in VARIANTS)
    for name in sorted(required):
        if not (directory / name).exists():
            failures.append({"kind": "missing_required_file", "file": name})

    receipt = _read_json(directory / "receipt.json", failures, "receipt_json") if (directory / "receipt.json").exists() else {}
    if not isinstance(receipt, dict):
        receipt = {}
    if receipt.get("mode") not in ("rehearsal", "live"):
        failures.append({"kind": "invalid_mode", "mode": receipt.get("mode")})
    if receipt.get("concordance_pass") is not True:
        failures.append({"kind": "concordance_not_passed", "value": receipt.get("concordance_pass")})

    listed = receipt.get("files_sha256")
    if not isinstance(listed, dict):
        failures.append({"kind": "missing_file_hashes"})
        listed = {}
    discovered = {path.name for path in directory.iterdir() if path.is_file() and path.name != "receipt.json"}
    if set(listed) != discovered:
        failures.append({"kind": "file_hash_inventory", "listed": sorted(listed),
                         "discovered": sorted(discovered)})
    for name in sorted(set(listed) | discovered):
        path = directory / name
        if name in listed and path.exists() and sha256(path) != listed[name]:
            failures.append({"kind": "file_hash_mismatch", "file": name})
        elif name in listed and not path.exists():
            failures.append({"kind": "hashed_file_missing", "file": name})

    concordance_path = directory / "concordance.json"
    concordance = _read_json(concordance_path, failures, "concordance_json") \
        if concordance_path.exists() else None
    concordance_ok = receipt.get("concordance_pass") is True and isinstance(concordance, dict)
    if concordance_path.exists() and receipt.get("concordance_sha256") != sha256(concordance_path):
        failures.append({"kind": "concordance_receipt_hash_mismatch",
                         "saved": receipt.get("concordance_sha256"),
                         "observed": sha256(concordance_path)})
        concordance_ok = False
    if isinstance(concordance, dict):
        for delay in ("0.0", "2.0"):
            item = concordance.get(delay)
            if not isinstance(item, dict):
                failures.append({"kind": "concordance_missing_delay", "delay": delay})
                concordance_ok = False
                continue
            if item.get("match") is not True:
                failures.append({"kind": "concordance_not_match", "delay": delay})
                concordance_ok = False
            differences = item.get("differences")
            if not isinstance(differences, list) or differences:
                failures.append({"kind": "concordance_differences", "delay": delay,
                                 "count": len(differences) if isinstance(differences, list) else None})
                concordance_ok = False
            candidate_digest = item.get("candidate_sha256")
            reference_digest = item.get("reference_sha256")
            if (not isinstance(candidate_digest, str) or len(candidate_digest) != 64
                    or not isinstance(reference_digest, str) or len(reference_digest) != 64
                    or candidate_digest != reference_digest):
                failures.append({"kind": "concordance_digest_mismatch", "delay": delay})
                concordance_ok = False
            receipt_concordance = receipt.get("concordance", {}).get(delay) \
                if isinstance(receipt.get("concordance"), dict) else None
            if isinstance(receipt_concordance, dict):
                for field in ("candidate_sha256", "reference_sha256"):
                    if receipt_concordance.get(field) != item.get(field):
                        failures.append({"kind": "concordance_receipt_binding", "delay": delay,
                                         "field": field})
                        concordance_ok = False
    else:
        failures.append({"kind": "concordance_not_object"})
    # Candidate/reference disagreement is a pre-scoring hard stop.
    if not concordance_ok:
        return {"checker": "check_a10g_evaluation", "directory": str(directory),
                "mode": receipt.get("mode"), "complete": False,
                "audit_failures": failures, "details": {}, "primary_calculated": None}

    frozen_path = directory / "frozen_parameters.json"
    frozen = _read_json(frozen_path, failures, "frozen_json") if frozen_path.exists() else {}
    if frozen_path.exists() and sha256(frozen_path) != FROZEN_SHA256:
        failures.append({"kind": "frozen_parameter_hash", "expected": FROZEN_SHA256,
                         "observed": sha256(frozen_path)})
    if not isinstance(frozen, dict) or set(frozen) != set(VARIANTS):
        failures.append({"kind": "frozen_variant_inventory", "observed": sorted(frozen) if isinstance(frozen, dict) else None})

    ledgers = {delay: _rows(directory / f"ledger-{delay}.json", failures, "ledger_json")
               for delay in ("0.0", "2.0") if (directory / f"ledger-{delay}.json").exists()}
    evidence = {delay: _rows(directory / f"evidence-{delay}.json", failures, "evidence_json")
                for delay in ("0.0", "2.0") if (directory / f"evidence-{delay}.json").exists()}
    _check_time_inputs(ledgers, evidence, failures)

    # Bind the saved candidate digest to the actual serialized ledger/evidence,
    # independently of the runner's reference implementation.
    for delay in ("0.0", "2.0"):
        item = concordance.get(delay) if isinstance(concordance, dict) else None
        try:
            observed_digest = concordance_digest(ledgers.get(delay, []), evidence.get(delay, []))
        except (TypeError, ValueError) as exc:
            failures.append({"kind": "concordance_digest_error", "delay": delay, "error": str(exc)})
            continue
        if isinstance(item, dict) and item.get("candidate_sha256") != observed_digest:
            failures.append({"kind": "candidate_concordance_digest_mismatch", "delay": delay,
                             "saved": item.get("candidate_sha256"), "observed": observed_digest})
    if any(f["kind"] in {"concordance_digest_error", "candidate_concordance_digest_mismatch"}
           for f in failures):
        return {"checker": "check_a10g_evaluation", "directory": str(directory),
                "mode": receipt.get("mode"), "complete": False,
                "audit_failures": failures, "details": {}, "primary_calculated": None}

    traces: dict[str, dict[int, dict[str, Any]]] = {}
    evidences: dict[str, dict[int, dict[str, Any]]] = {}
    for delay in ("0.0", "2.0"):
        traces[delay] = {}
        evidences[delay] = {}
        for row in ledgers.get(delay, []):
            ident = row.get("emission_index")
            if not isinstance(ident, int) or ident in traces[delay]:
                failures.append({"kind": "duplicate_or_bad_ledger_id", "delay": delay, "id": ident})
            else:
                traces[delay][ident] = row
        for row in evidence.get(delay, []):
            ident = row.get("emission_index")
            if not isinstance(ident, int) or ident in evidences[delay]:
                failures.append({"kind": "duplicate_or_bad_evidence_id", "delay": delay, "id": ident})
            else:
                evidences[delay][ident] = row
        for ident in sorted(set(evidences[delay]) - set(traces[delay])):
            failures.append({"kind": "evidence_without_ledger", "delay": delay,
                             "emission_index": ident})
        for ident in sorted(set(traces[delay]) & set(evidences[delay])):
            lhs, rhs = traces[delay][ident].get("issue_time"), evidences[delay][ident].get("issue_time")
            if finite(lhs) and finite(rhs) and abs(float(lhs) - float(rhs)) > TOL:
                failures.append({"kind": "evidence_issue_time_mismatch", "delay": delay,
                                 "emission_index": ident, "ledger": lhs, "evidence": rhs})

    score_rows: dict[str, list[dict[str, Any]]] = {}
    for variant in VARIANTS:
        path = directory / f"{variant}-scores.json"
        score_rows[variant] = _rows(path, failures, "scores_json") if path.exists() else []

    report_details: dict[str, Any] = {}
    for variant in VARIANTS:
        spec = frozen.get(variant) if isinstance(frozen, dict) else None
        delay = "2.0" if variant == "delay_2" else "0.0"
        features, evs = traces.get(delay, {}), evidences.get(delay, {})
        expected: set[int] = set()
        for ident, feature in features.items():
            ev = evs.get(ident)
            if ev is None:
                failures.append({"kind": "missing_evidence", "variant": variant,
                                 "delay": delay, "emission_index": ident})
                continue
            if ev.get("kind") == "excluded":
                continue
            nodes = endpoint_nodes(feature, spec.get("endpoint_mode", "point"), int(spec.get("nodes", 1))) \
                if isinstance(spec, dict) and feature.get("landmark_available") is True else None
            endpoint = nodes is not None
            current_mark = current_durations(feature, nodes) is not None
            if isinstance(spec, dict) and spec.get("joint_marks") and not (endpoint and q_available(feature)
                                                                             and current_mark and previous_duration_available(feature)):
                continue
            expected.add(ident)
        rows_by_id: dict[int, dict[str, Any]] = {}
        for row in score_rows[variant]:
            ident = row.get("emission_index")
            if not isinstance(ident, int) or ident in rows_by_id:
                failures.append({"kind": "duplicate_or_bad_score_id", "variant": variant, "id": ident})
            else:
                rows_by_id[ident] = row
        if set(rows_by_id) != expected:
            failures.append({"kind": "score_population", "variant": variant,
                             "expected": len(expected), "observed": len(rows_by_id),
                             "missing": sorted(expected - set(rows_by_id))[:10],
                             "extra": sorted(set(rows_by_id) - expected)[:10]})

        score_errors = route_errors = gain_errors = 0
        max_error = 0.0
        for ident, row in rows_by_id.items():
            feature, ev = features.get(ident), evs.get(ident)
            if feature is None or ev is None or not isinstance(spec, dict):
                if feature is None or ev is None:
                    failures.append({"kind": "score_missing_trace", "variant": variant,
                                     "emission_index": ident})
                continue
            if not finite(row.get("issue_time")) or abs(float(row["issue_time"]) - float(feature["issue_time"])) > TOL:
                failures.append({"kind": "score_issue_time_mismatch", "variant": variant,
                                 "emission_index": ident, "saved": row.get("issue_time"),
                                 "ledger": feature.get("issue_time")})
            nodes = endpoint_nodes(feature, spec["endpoint_mode"], int(spec["nodes"])) \
                if feature.get("landmark_available") is True else None
            endpoint = nodes is not None
            durations = current_durations(feature, nodes)
            current_mark = durations is not None
            for model_name in MODELS:
                try:
                    route = route_for(model_name, spec["models"][model_name], feature, endpoint, current_mark)
                    if row.get(f"{model_name}_route") != route:
                        route_errors += 1
                    predicted = conditional_score(feature, ev, spec, route)
                    if not finite(row.get(model_name)):
                        score_errors += 1
                    else:
                        error = abs(predicted - float(row[model_name]))
                        max_error = max(max_error, error)
                        if error > TOL:
                            score_errors += 1
                    if _zero_mark(spec["models"][model_name]) and route in ("M2", "M3", "P3") \
                            and finite(row.get(model_name)) and finite(row.get("M2")) \
                            and abs(float(row[model_name]) - float(row["M2"])) > TOL:
                        failures.append({"kind": "exact_zero_route_score", "variant": variant,
                                         "emission_index": ident, "model": model_name})
                except Exception as exc:
                    failures.append({"kind": "score_recompute_error", "variant": variant,
                                     "emission_index": ident, "model": model_name, "error": str(exc)})
            for lhs, rhs, field in (("M3", "M2", "gain_M3_M2"), ("M2", "M0", "gain_M2_M0"),
                                    ("M3", "P3", "gain_M3_P3"), ("P3", "M2", "gain_P3_M2")):
                if not finite(row.get(field)) or not finite(row.get(lhs)) or not finite(row.get(rhs)) \
                        or abs(float(row[field]) - (float(row[lhs]) - float(row[rhs]))) > TOL:
                    gain_errors += 1
        if score_errors:
            failures.append({"kind": "score_mismatch", "variant": variant, "count": score_errors,
                             "max_abs_error": max_error})
        if route_errors:
            failures.append({"kind": "route_mismatch", "variant": variant, "count": route_errors})
        if gain_errors:
            failures.append({"kind": "gain_mismatch", "variant": variant, "count": gain_errors})
        report_details[variant] = {"expected_rows": len(expected), "observed_rows": len(rows_by_id),
                                   "max_abs_score_error": max_error}

    primary = _read_json(directory / "primary.json", failures, "primary_json") if (directory / "primary.json").exists() else None
    try:
        calculated = primary_interval(score_rows.get("primary", []))
        _compare_primary(primary, calculated, failures)
    except Exception as exc:
        calculated = None
        failures.append({"kind": "primary_interval_error", "error": str(exc)})

    return {"checker": "check_a10g_evaluation", "directory": str(directory),
            "mode": receipt.get("mode"), "complete": not failures,
            "audit_failures": failures, "details": report_details,
            "primary_calculated": calculated}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.directory)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"complete": report["complete"], "failure_count": len(report["audit_failures"])}, sort_keys=True))
    return 0 if report["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
