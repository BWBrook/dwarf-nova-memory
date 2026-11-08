"""Censoring-aware lognormal forecast models for the prefix ledger.

This module is deliberately a statistical prototype.  It fits conditional
waiting-time distributions to the prefix ledger and does not infer missed
events, latent states, or physical disc parameters.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.optimize import minimize
from scipy.special import log_ndtr, logsumexp


_KINDS = {"interval", "right_censored", "excluded"}
_MODEL_NAMES = ("M0", "M1", "M2", "M3")
_BOUNDS = ((-2.0, 8.0), (-5.0, 5.0), (-5.0, 5.0), (-4.0, 2.0))
_EPS = 1e-10


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _as_float(value: Any, label: str) -> float:
    if value is None or not _finite(value):
        raise ValueError(f"{label} must be finite")
    return float(value)


def _optional_float(value: Any, label: str) -> float | None:
    if value is None:
        return None
    return _as_float(value, label)


def _log_cdf(t: float, mu: float, sigma: float) -> float:
    if t <= 0.0:
        return -math.inf
    return float(log_ndtr((math.log(t) - mu) / sigma))


def _log_survival(t: float, mu: float, sigma: float) -> float:
    if t <= 0.0:
        return 0.0
    return float(log_ndtr(-(math.log(t) - mu) / sigma))


def _logdiffexpm1(log_hi: float, log_lo: float) -> float:
    """Return log(exp(log_hi)-exp(log_lo)) without probability flooring."""
    if log_lo == -math.inf:
        return log_hi
    if not (math.isfinite(log_hi) and math.isfinite(log_lo)) or log_lo >= log_hi:
        return -math.inf
    return log_hi + math.log(-math.expm1(log_lo - log_hi))


def _log_interval(lower: float, upper: float, mu: float, sigma: float) -> float:
    if not (_finite(lower) and _finite(upper)) or lower < 0.0 or upper <= lower:
        raise ValueError("interval waiting times require 0 <= lower < upper")
    if lower >= math.exp(mu):
        result = _logdiffexpm1(_log_survival(lower, mu, sigma), _log_survival(upper, mu, sigma))
    else:
        result = _logdiffexpm1(_log_cdf(upper, mu, sigma), _log_cdf(lower, mu, sigma))
    if result == -math.inf:
        raise ValueError("interval probability underflowed to zero")
    return result


def _validate_evidence(evidence: Sequence[Mapping[str, Any]], cutoff: float) -> dict[int, dict[str, Any]]:
    indexed: dict[int, dict[str, Any]] = {}
    for row in evidence:
        if "computed_as_of" not in row or row["computed_as_of"] is None:
            raise ValueError("every evidence row requires computed_as_of")
        computed = _as_float(row["computed_as_of"], "evidence.computed_as_of")
        if computed > cutoff:
            raise ValueError("evidence.computed_as_of is after training_cutoff")
        if "evidence_available_at" not in row or row["evidence_available_at"] is None:
            raise ValueError("every evidence row requires evidence_available_at")
        available = _as_float(row["evidence_available_at"], "evidence.evidence_available_at")
        if available > cutoff:
            raise ValueError("evidence.evidence_available_at is after training_cutoff")
        index = int(row["emission_index"])
        if index in indexed:
            raise ValueError(f"duplicate evidence emission_index {index}")
        kind = row.get("kind")
        if kind not in _KINDS:
            raise ValueError(f"unknown evidence kind {kind!r}")
        issue = _as_float(row.get("issue_time"), "evidence.issue_time")
        if issue >= cutoff:
            raise ValueError("evidence.issue_time is not before training_cutoff")
        indexed[index] = dict(row, computed_as_of=computed, evidence_available_at=available,
                              issue_time=issue, emission_index=index)
    return indexed


def _validate_features(features: Sequence[Mapping[str, Any]], cutoff: float) -> dict[int, dict[str, Any]]:
    indexed: dict[int, dict[str, Any]] = {}
    for row in features:
        if "issue_time" not in row:
            raise ValueError("every feature row requires issue_time")
        issue = _as_float(row["issue_time"], "feature.issue_time")
        if issue >= cutoff:
            raise ValueError("feature.issue_time is not before training_cutoff")
        index = int(row["emission_index"])
        if index in indexed:
            raise ValueError(f"duplicate feature emission_index {index}")
        indexed[index] = dict(row, issue_time=issue, emission_index=index)
    return indexed


def _endpoint_nodes(feature: Mapping[str, Any], endpoint_mode: str, nodes: int) -> np.ndarray | None:
    if feature.get("landmark_available") is False:
        return None
    issue = _as_float(feature.get("issue_time"), "feature.issue_time")
    if endpoint_mode == "point":
        end = _optional_float(feature.get("end_t"), "feature.end_t")
        if end is None:
            return None
        if end > issue + _EPS:
            raise ValueError("known end_t is after issue_time")
        return np.array([end], dtype=float)
    lo = _optional_float(feature.get("end_lo"), "feature.end_lo")
    hi = _optional_float(feature.get("end_hi"), "feature.end_hi")
    if lo is None or hi is None:
        return None
    hi = min(hi, issue)
    if hi < lo - _EPS:
        raise ValueError("end interval has no pre-landmark support")
    if hi - lo <= _EPS:
        return np.array([lo], dtype=float)
    return np.linspace(lo, hi, nodes, dtype=float)


def _duration_value(feature: Mapping[str, Any], endpoint: float, mark_mode: str) -> float | None:
    onset = _optional_float(feature.get("onset_t"), "feature.onset_t")
    if onset is not None:
        duration = endpoint - onset
    else:
        duration = _optional_float(feature.get("duration"), "feature.duration")
    if duration is None:
        return None
    if duration <= 0.0:
        raise ValueError("duration must be positive")
    return duration


def _previous_value(feature: Mapping[str, Any]) -> float | None:
    if feature.get("previous_gap_covered") is not True:
        return None
    gap = _optional_float(feature.get("previous_gap"), "feature.previous_gap")
    if gap is None:
        return None
    if gap <= 0.0:
        raise ValueError("previous_gap must be positive when covered")
    return gap


def _duration_domain(feature: Mapping[str, Any], endpoints: np.ndarray | None) -> tuple[bool, np.ndarray | None, str]:
    """Check the mark domain without evaluating log-duration at invalid nodes."""
    if endpoints is None or len(endpoints) == 0:
        return False, None, "missing_landmark"
    onset = _optional_float(feature.get("onset_t"), "feature.onset_t")
    if onset is not None:
        margins = np.asarray(endpoints, dtype=float) - onset
        return bool(np.all(margins > 0.0)), margins, "onset"
    duration = _optional_float(feature.get("duration"), "feature.duration")
    if duration is None:
        return False, None, "missing_mark"
    margins = np.asarray([duration], dtype=float)
    return bool(duration > 0.0), margins, "stored_duration"


def _duration_availability(feature: Mapping[str, Any], endpoints: np.ndarray | float | None,
                           mark_mode: str = "log_duration") -> bool:
    values = None if endpoints is None else np.atleast_1d(np.asarray(endpoints, dtype=float))
    return _duration_domain(feature, values)[0]


def _covariate_values(duration: float, mark_mode: str, transform: Mapping[str, Any]) -> dict[str, float]:
    log_d = math.log(duration)
    if mark_mode == "log_duration":
        return {"duration": (log_d - float(transform["duration_center"])) / float(transform["duration_scale"])}
    typ = float(duration >= 12.0)
    centers = transform["duration_type_centers"]
    center = float(centers[str(int(typ))])
    return {
        "duration_type": typ,
        "duration_within": (log_d - center) / float(transform["duration_within_scale"]),
    }


def _feature_vector(feature: Mapping[str, Any], endpoint: float, model_name: str,
                    mark_mode: str, transform: Mapping[str, Any]) -> dict[str, float] | None:
    values: dict[str, float] = {}
    if model_name in ("M1", "M3"):
        duration = _duration_value(feature, endpoint, mark_mode)
        if duration is None:
            return None
        values.update(_covariate_values(duration, mark_mode, transform))
    if model_name in ("M2", "M3"):
        previous = _previous_value(feature)
        if previous is None:
            return None
        values["previous_gap"] = (math.log(previous) - float(transform["previous_center"])) / float(transform["previous_scale"])
    return values


def _model_terms(model_name: str, mark_mode: str) -> tuple[str, ...]:
    duration = ("duration",) if mark_mode == "log_duration" else ("duration_type", "duration_within")
    return {"M0": (), "M1": duration, "M2": ("previous_gap",), "M3": duration + ("previous_gap",)}[model_name]


def _counts(evidence: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    result = {kind: 0 for kind in _KINDS}
    for row in evidence:
        result[row["kind"]] += 1
    return result


def _remaining_loglik(evidence: Mapping[str, Any], mu: float, sigma: float) -> float:
    issue = _as_float(evidence.get("issue_time"), "evidence.issue_time")
    if evidence["kind"] == "interval":
        lo = _as_float(evidence.get("onset_lo"), "evidence.onset_lo") - issue
        hi = _as_float(evidence.get("onset_hi"), "evidence.onset_hi") - issue
        return _log_interval(lo, hi, mu, sigma)
    censor = _as_float(evidence.get("censor_at"), "evidence.censor_at") - issue
    if censor < -_EPS:
        raise ValueError("censor_at is before issue_time")
    if censor <= _EPS:
        return 0.0
    return _log_survival(censor, mu, sigma)


def _conditional_node_loglik(evidence: Mapping[str, Any], endpoint: float, mu: float, sigma: float) -> tuple[float, float]:
    issue = _as_float(evidence.get("issue_time"), "evidence.issue_time")
    age = issue - endpoint
    if age < -_EPS:
        raise ValueError("endpoint is after issue_time")
    denominator = _log_survival(max(0.0, age), mu, sigma)
    if evidence["kind"] == "interval":
        lo = _as_float(evidence.get("onset_lo"), "evidence.onset_lo") - endpoint
        hi = _as_float(evidence.get("onset_hi"), "evidence.onset_hi") - endpoint
        if lo < age - _EPS:
            raise ValueError("onset interval begins before the landmark")
        numerator = _log_interval(max(0.0, lo), hi, mu, sigma)
    else:
        censor = _as_float(evidence.get("censor_at"), "evidence.censor_at") - endpoint
        if censor < age - _EPS:
            raise ValueError("censoring precedes the landmark")
        numerator = 0.0 if censor <= _EPS else _log_survival(max(0.0, censor), mu, sigma)
    return numerator, denominator


def _node_loglik(feature: Mapping[str, Any], evidence: Mapping[str, Any], endpoints: np.ndarray,
                 coefficients: np.ndarray, terms: tuple[str, ...], transform: Mapping[str, Any],
                 mark_mode: str) -> float:
    log_num = []
    log_den = []
    for endpoint in endpoints:
        duration = _duration_value(feature, float(endpoint), mark_mode) if any(
            t.startswith("duration") for t in terms) else None
        previous = _previous_value(feature) if "previous_gap" in terms else None
        if any(t.startswith("duration") for t in terms) and duration is None:
            raise ValueError("duration is missing for a duration model")
        if "previous_gap" in terms and previous is None:
            raise ValueError("previous_gap is missing for a previous-gap model")
        covariates = {}
        if duration is not None:
            covariates.update(_covariate_values(duration, mark_mode, transform))
        if previous is not None:
            covariates["previous_gap"] = (math.log(previous) - float(transform["previous_center"])) / float(transform["previous_scale"])
        mu = float(coefficients[0]) + sum(float(coefficients[i + 1]) * covariates[t]
                                          for i, t in enumerate(terms))
        numerator, denominator = _conditional_node_loglik(evidence, float(endpoint), mu,
                                                          math.exp(float(coefficients[-1])))
        log_num.append(numerator)
        log_den.append(denominator)
    weights = -math.log(len(endpoints))
    return float(logsumexp(np.asarray(log_num) + weights) - logsumexp(np.asarray(log_den) + weights))


def _logdiffexpm1_array(log_hi: np.ndarray, log_lo: np.ndarray) -> np.ndarray:
    result = np.full(np.broadcast_shapes(log_hi.shape, log_lo.shape), -math.inf, dtype=float)
    hi, lo = np.broadcast_arrays(log_hi, log_lo)
    valid = np.isfinite(hi) & np.isfinite(lo) & (lo < hi)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        result[valid] = hi[valid] + np.log(-np.expm1(lo[valid] - hi[valid]))
    result[np.isneginf(lo)] = hi[np.isneginf(lo)]
    return result


def _log_cdf_array(times: np.ndarray, mu: np.ndarray, sigma: float) -> np.ndarray:
    safe_times = np.where(times > 0.0, times, 1.0)
    result = log_ndtr((np.log(safe_times) - mu) / sigma)
    return np.where(times > 0.0, result, -math.inf)


def _log_survival_array(times: np.ndarray, mu: np.ndarray, sigma: float) -> np.ndarray:
    safe_times = np.where(times > 0.0, times, 1.0)
    result = log_ndtr(-(np.log(safe_times) - mu) / sigma)
    return np.where(times > 0.0, result, 0.0)


def _log_interval_array(lower: np.ndarray, upper: np.ndarray, mu: np.ndarray,
                        sigma: float) -> np.ndarray:
    use_survival = lower >= np.exp(mu)
    cdf_result = _logdiffexpm1_array(_log_cdf_array(upper, mu, sigma),
                                     _log_cdf_array(lower, mu, sigma))
    survival_result = _logdiffexpm1_array(_log_survival_array(lower, mu, sigma),
                                          _log_survival_array(upper, mu, sigma))
    return np.where(use_survival, survival_result, cdf_result)


@dataclass(frozen=True)
class _PreparedLikelihood:
    design: np.ndarray
    interval_lower: np.ndarray
    interval_upper: np.ndarray
    censor_time: np.ndarray
    age: np.ndarray
    is_interval: np.ndarray
    node_log_weights: np.ndarray

    def objective(self, theta: np.ndarray) -> float:
        sigma = math.exp(float(theta[-1]))
        if not math.isfinite(sigma):
            return 1e100
        mu = float(theta[0]) + np.einsum("nkp,p->nk", self.design, theta[1:-1])
        numerator_interval = _log_interval_array(self.interval_lower, self.interval_upper, mu, sigma)
        numerator_censored = _log_survival_array(self.censor_time, mu, sigma)
        numerator_censored = np.where(self.censor_time <= _EPS, 0.0, numerator_censored)
        numerator = np.where(self.is_interval[:, None], numerator_interval, numerator_censored)
        denominator = _log_survival_array(self.age, mu, sigma)
        row_numerator = logsumexp(numerator + self.node_log_weights, axis=1)
        row_denominator = logsumexp(denominator + self.node_log_weights, axis=1)
        value = -float(np.sum(row_numerator - row_denominator))
        return value if math.isfinite(value) else 1e100


def _prepare_likelihood(rows: Sequence[Mapping[str, Any]], terms: tuple[str, ...],
                        transform: Mapping[str, Any], mark_mode: str) -> _PreparedLikelihood:
    n_rows = len(rows)
    n_nodes = max(len(row["endpoints"]) for row in rows)
    design = np.zeros((n_rows, n_nodes, len(terms)), dtype=float)
    lower = np.zeros((n_rows, n_nodes), dtype=float)
    upper = np.ones((n_rows, n_nodes), dtype=float)
    censor = np.zeros((n_rows, n_nodes), dtype=float)
    age = np.zeros((n_rows, n_nodes), dtype=float)
    node_log_weights = np.full((n_rows, n_nodes), -math.inf, dtype=float)
    is_interval = np.zeros(n_rows, dtype=bool)
    for i, row in enumerate(rows):
        feature, evidence, endpoints = row["feature"], row["evidence"], row["endpoints"]
        issue = float(evidence["issue_time"])
        is_interval[i] = evidence["kind"] == "interval"
        node_log_weights[i, :len(endpoints)] = -math.log(len(endpoints))
        for j, endpoint in enumerate(endpoints):
            endpoint = float(endpoint)
            duration = _duration_value(feature, endpoint, mark_mode) if any(
                term.startswith("duration") for term in terms) else None
            previous = _previous_value(feature) if "previous_gap" in terms else None
            if any(term.startswith("duration") for term in terms) and duration is None:
                raise ValueError("duration is missing for a duration model")
            if "previous_gap" in terms and previous is None:
                raise ValueError("previous_gap is missing for a previous-gap model")
            covariates = {}
            if duration is not None:
                covariates.update(_covariate_values(duration, mark_mode, transform))
            if previous is not None:
                covariates["previous_gap"] = (math.log(previous) - float(transform["previous_center"])) / float(transform["previous_scale"])
            design[i, j, :] = [covariates[term] for term in terms]
            current_age = issue - endpoint
            if current_age < -_EPS:
                raise ValueError("endpoint is after issue_time")
            age[i, j] = max(0.0, current_age)
            if is_interval[i]:
                lower[i, j] = float(evidence["onset_lo"]) - endpoint
                upper[i, j] = float(evidence["onset_hi"]) - endpoint
                if lower[i, j] < age[i, j] - _EPS or upper[i, j] <= lower[i, j]:
                    raise ValueError("invalid onset interval for landmark")
            else:
                censor[i, j] = float(evidence["censor_at"]) - endpoint
                if censor[i, j] < age[i, j] - _EPS:
                    raise ValueError("censoring precedes the landmark")
    return _PreparedLikelihood(design, lower, upper, censor, age, is_interval, node_log_weights)


def _scalar_model_objective(theta: np.ndarray, rows: Sequence[Mapping[str, Any]], terms: tuple[str, ...],
                            transform: Mapping[str, Any], mark_mode: str) -> float:
    try:
        value = -sum(_node_loglik(row["feature"], row["evidence"], row["endpoints"], theta,
                                  terms, transform, mark_mode) for row in rows)
    except (ValueError, FloatingPointError, OverflowError):
        return 1e100
    return float(value) if math.isfinite(value) else 1e100


@dataclass(frozen=True)
class _PreparedRemaining:
    interval_lower: np.ndarray
    interval_upper: np.ndarray
    censor_time: np.ndarray
    is_interval: np.ndarray

    def objective(self, theta: np.ndarray) -> float:
        mu, log_sigma = float(theta[0]), float(theta[1])
        sigma = math.exp(log_sigma)
        if not math.isfinite(sigma):
            return 1e100
        interval = _log_interval_array(self.interval_lower, self.interval_upper,
                                       np.full_like(self.interval_lower, mu), sigma)
        censored = _log_survival_array(self.censor_time,
                                       np.full_like(self.censor_time, mu), sigma)
        censored = np.where(self.censor_time <= _EPS, 0.0, censored)
        terms = np.where(self.is_interval, interval, censored)
        value = -float(np.sum(terms))
        return value if math.isfinite(value) else 1e100


def _prepare_remaining(rows: Sequence[Mapping[str, Any]]) -> _PreparedRemaining:
    lower, upper, censor = [], [], []
    is_interval = []
    for row in rows:
        evidence = row["evidence"]
        issue = float(evidence["issue_time"])
        if evidence["kind"] == "interval":
            lo = float(evidence["onset_lo"]) - issue
            hi = float(evidence["onset_hi"]) - issue
            if lo < 0.0 or hi <= lo:
                raise ValueError("invalid remaining-wait interval")
            lower.append(lo)
            upper.append(hi)
            censor.append(0.0)
            is_interval.append(True)
        else:
            value = float(evidence["censor_at"]) - issue
            if value < -_EPS:
                raise ValueError("censoring precedes issue_time")
            lower.append(0.0)
            upper.append(1.0)
            censor.append(value)
            is_interval.append(False)
    return _PreparedRemaining(np.asarray(lower), np.asarray(upper), np.asarray(censor),
                              np.asarray(is_interval, dtype=bool))


def _r0_objective(theta: np.ndarray, rows: Sequence[Mapping[str, Any]]) -> float:
    mu, log_sigma = float(theta[0]), float(theta[1])
    sigma = math.exp(log_sigma)
    if not (math.isfinite(mu) and math.isfinite(sigma)):
        return 1e100
    try:
        value = -sum(_remaining_loglik(row["evidence"], mu, sigma) for row in rows)
    except (ValueError, FloatingPointError):
        return 1e100
    return float(value) if math.isfinite(value) else 1e100


def _fit_r0(rows: Sequence[Mapping[str, Any]], counts: Mapping[str, int]) -> "ForecastModel":
    if len(rows) < 2:
        raise ValueError("R0 requires at least two non-excluded evidence rows")
    starts = _initial_starts(rows, (), {}, "log_duration", r0=True)
    prepared = _prepare_remaining(rows)
    results = []
    for start in starts:
        result = minimize(prepared.objective, start, method="L-BFGS-B",
                          bounds=(_BOUNDS[0], _BOUNDS[3]))
        results.append(result)
    best = _choose_result(results, "R0")
    return ForecastModel(
        name="R0", intercept=float(best.x[0]), coefficients={}, sigma=math.exp(float(best.x[1])),
        centers={}, scales={}, n_fit=len(rows), terms=(), metadata={
            "fit_kind": "remaining_wait_at_issue", "n_fit": len(rows),
            "counts": dict(counts), "convergence": _diagnostics(results, best, _BOUNDS[:1] + (_BOUNDS[3],)),
        })


def _initial_starts(rows: Sequence[Mapping[str, Any]], terms: tuple[str, ...], transform: Mapping[str, Any],
                    mark_mode: str, r0: bool = False) -> list[np.ndarray]:
    ys: list[float] = []
    paired_y: list[float] = []
    xrows: list[tuple[float, ...]] = []
    for row in rows:
        evidence = row["evidence"]
        issue = float(evidence["issue_time"])
        if evidence["kind"] == "interval":
            lo = float(evidence["onset_lo"]) - issue
            hi = float(evidence["onset_hi"]) - issue
            if lo >= 0 and hi > lo:
                ys.append(math.log((lo + hi) / 2.0))
                if not r0:
                    endpoint = float(row["endpoints"][0])
                    cov = _feature_vector(row["feature"], endpoint, row["model_name"], mark_mode, transform) or {}
                    xrows.append(tuple(cov[t] for t in terms))
                    paired_y.append(math.log((lo + hi) / 2.0))
        elif evidence["kind"] == "right_censored":
            censor = float(evidence["censor_at"]) - issue
            if censor > 0:
                ys.append(math.log(censor))
    if not ys:
        ys = [0.0]
    if r0:
        y = float(np.mean(ys))
        s = max(0.2, min(2.0, float(np.std(ys)) or 0.5))
        return [np.array([y, math.log(s)]), np.array([float(np.median(ys)), math.log(max(0.25, s * 0.8))])]
    y = np.asarray(ys, dtype=float)
    x = np.asarray(xrows, dtype=float) if xrows else np.empty((0, len(terms)))
    paired = np.asarray(paired_y, dtype=float)
    slopes = np.zeros(len(terms), dtype=float)
    intercept = float(np.mean(y))
    if len(x) >= len(terms) + 1 and x.shape[1]:
        design = np.column_stack([np.ones(len(x)), x])
        try:
            beta = np.linalg.lstsq(design, paired, rcond=None)[0]
            intercept, slopes = float(beta[0]), np.asarray(beta[1:], dtype=float)
        except np.linalg.LinAlgError:
            pass
    init_residual = paired - intercept - (x @ slopes if len(x) else 0.0)
    scale = max(0.25, min(2.0, float(np.std(init_residual)) if len(init_residual) else 0.5))
    first = np.concatenate(([intercept], slopes, [math.log(scale)]))
    second = np.concatenate(([float(np.median(y))], np.zeros(len(terms)), [math.log(max(0.25, scale * 0.8))]))
    return [first, second]


def _choose_result(results: Sequence[Any], name: str) -> Any:
    successful = [r for r in results if bool(r.success) and np.all(np.isfinite(r.x))
                  and math.isfinite(float(r.fun)) and float(r.fun) < 1e99]
    if not successful:
        messages = "; ".join(str(r.message) for r in results)
        raise ValueError(f"{name} optimization failed: {messages}")
    best = min(successful, key=lambda r: float(r.fun))
    if best.jac is None or not np.all(np.isfinite(np.asarray(best.jac, dtype=float))):
        raise ValueError(f"{name} optimization returned a non-finite gradient")
    return best


def _diagnostics(results: Sequence[Any], best: Any, bounds: Sequence[tuple[float, float]]) -> dict[str, Any]:
    names = ["intercept"] + [f"coefficient_{i}" for i in range(len(best.x) - 2)] + ["log_sigma"]
    boundary = [names[i] for i, (value, bound) in enumerate(zip(best.x, bounds))
                if abs(float(value) - bound[0]) < 1e-6 or abs(float(value) - bound[1]) < 1e-6]
    return {"success": bool(best.success), "message": str(best.message), "objective": float(best.fun),
            "gradient_finite": bool(best.jac is not None and np.all(np.isfinite(best.jac))),
            "boundary_parameters": boundary,
            "starts": [{"success": bool(r.success), "objective": float(r.fun) if math.isfinite(float(r.fun)) else None,
                         "message": str(r.message)} for r in results]}


@dataclass(frozen=True)
class ForecastModel:
    name: str
    intercept: float
    coefficients: dict[str, float]
    sigma: float
    centers: dict[str, Any]
    scales: dict[str, Any]
    n_fit: int
    terms: tuple[str, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "intercept": self.intercept, "coefficients": dict(self.coefficients),
                "sigma": self.sigma, "centers": self.centers, "scales": self.scales,
                "n_fit": self.n_fit, "terms": list(self.terms), "metadata": self.metadata}


def _model_mu(model: ForecastModel, feature: Mapping[str, Any], endpoint: float,
              mark_mode: str) -> float:
    transform = {"duration_center": model.centers.get("duration", 0.0),
                 "duration_scale": model.scales.get("duration", 1.0),
                 "duration_type_centers": model.centers.get("duration_type", {"0": 0.0, "1": 0.0}),
                 "duration_within_scale": model.scales.get("duration_within", 1.0),
                 "previous_center": model.centers.get("previous_gap", 0.0),
                 "previous_scale": model.scales.get("previous_gap", 1.0)}
    values = _feature_vector(feature, endpoint, model.name, mark_mode, transform) or {}
    return model.intercept + sum(model.coefficients[t] * values[t] for t in model.terms)


def duration_domain_diagnostics(ledger: Sequence[Mapping[str, Any]], *,
                               endpoint_mode: str = "point", nodes: int = 5) -> dict[str, Any]:
    """Summarize positive-duration support for a ledger and endpoint variant."""
    if endpoint_mode not in {"point", "uniform_end"} or not isinstance(nodes, int) or nodes < 1:
        raise ValueError("invalid endpoint variant")
    known = 0
    margins: list[float] = []
    nonpositive: list[int] = []
    missing: list[int] = []
    point_invalid: list[int] = []
    interval_only: list[int] = []
    variant_missing: list[int] = []
    for feature in ledger:
        emission = int(feature["emission_index"])
        onset = _optional_float(feature.get("onset_t"), "feature.onset_t")
        point_end = _optional_float(feature.get("end_t"), "feature.end_t")
        point_margin = point_end - onset if onset is not None and point_end is not None else None
        if point_margin is not None and point_margin <= 0.0:
            point_invalid.append(emission)

        interval_nodes: np.ndarray | None = None
        lo = _optional_float(feature.get("end_lo"), "feature.end_lo")
        hi = _optional_float(feature.get("end_hi"), "feature.end_hi")
        issue = _optional_float(feature.get("issue_time"), "feature.issue_time")
        if lo is not None and hi is not None and issue is not None:
            hi = min(hi, issue)
            if hi >= lo - _EPS:
                interval_nodes = np.array([lo], dtype=float) if hi - lo <= _EPS else np.linspace(lo, hi, nodes)
        if onset is not None and interval_nodes is not None:
            interval_margins = interval_nodes - onset
            if point_margin is not None and point_margin > 0.0 and np.any(interval_margins <= 0.0):
                interval_only.append(emission)

        try:
            endpoints = _endpoint_nodes(feature, endpoint_mode, nodes)
        except ValueError:
            endpoints = None
        if endpoints is not None:
            known += 1
        available, active_margins, source = _duration_domain(feature, endpoints)
        if active_margins is not None:
            margins.extend(float(value) for value in active_margins)
            if np.any(active_margins <= 0.0):
                nonpositive.append(emission)
        elif source == "missing_mark":
            missing.append(emission)
        elif source == "missing_landmark":
            variant_missing.append(emission)
            if onset is None and _optional_float(feature.get("duration"), "feature.duration") is None:
                missing.append(emission)

    return {
        "endpoint_mode": endpoint_mode,
        "nodes": nodes,
        "known_landmark_count": known,
        "nonpositive_mark_count": len(nonpositive),
        "nonpositive_mark_emission_indices": nonpositive,
        "missing_mark_count": len(missing),
        "missing_mark_emission_indices": missing,
        "point_invalid_count": len(point_invalid),
        "point_invalid_emission_indices": point_invalid,
        "interval_only_overlap_count": len(interval_only),
        "interval_only_overlap_emission_indices": interval_only,
        "variant_missing_landmark_count": len(variant_missing),
        "variant_missing_landmark_emission_indices": variant_missing,
        "min_margin": min(margins) if margins else None,
    }


@dataclass(frozen=True)
class ForecastBundle:
    models: dict[str, ForecastModel]
    r0: ForecastModel
    endpoint_mode: str
    nodes: int
    mark_mode: str
    counts: dict[str, int]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"models": {name: model.to_dict() for name, model in self.models.items()},
                "r0": self.r0.to_dict(), "endpoint_mode": self.endpoint_mode, "nodes": self.nodes,
                "mark_mode": self.mark_mode, "counts": dict(self.counts), "metadata": self.metadata}

    def duration_domain_diagnostics(self, ledger: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        return duration_domain_diagnostics(ledger, endpoint_mode=self.endpoint_mode, nodes=self.nodes)

    def route(self, feature: Mapping[str, Any], model_name: str) -> str:
        """Return the fitted model actually used after missing-mark fallback."""
        if model_name not in self.models:
            raise ValueError(f"unknown model {model_name!r}")
        endpoints = _endpoint_nodes(feature, self.endpoint_mode, self.nodes)
        if endpoints is None:
            return "R0"
        previous_ok = _previous_value(feature) is not None
        if model_name == "M0":
            return "M0"
        if model_name == "M2":
            return "M2" if previous_ok else "M0"
        duration_ok = _duration_availability(feature, endpoints, self.mark_mode)
        if model_name == "M1":
            return "M1" if duration_ok else "M0"
        if model_name == "M3":
            return "M3" if duration_ok and previous_ok else "M2" if previous_ok else "M1" if duration_ok else "M0"
        return "M0"

    def score(self, feature: Mapping[str, Any], evidence: Mapping[str, Any], model_name: str) -> float | None:
        if evidence.get("kind") == "excluded":
            return None
        if model_name not in self.models:
            raise ValueError(f"unknown model {model_name!r}")
        if int(feature["emission_index"]) != int(evidence["emission_index"]):
            raise ValueError("feature and evidence emission_index do not match")
        if float(feature["issue_time"]) != float(evidence["issue_time"]):
            raise ValueError("feature and evidence issue_time do not match")
        selected = self.route(feature, model_name)
        endpoints = _endpoint_nodes(feature, self.endpoint_mode, self.nodes)
        if selected == "R0":
            return float(_remaining_loglik(evidence, self.r0.intercept, self.r0.sigma))
        model = self.models[selected]
        log_num, log_den = [], []
        transform = {"duration_center": model.centers.get("duration", 0.0),
                     "duration_scale": model.scales.get("duration", 1.0),
                     "duration_type_centers": model.centers.get("duration_type", {"0": 0.0, "1": 0.0}),
                     "duration_within_scale": model.scales.get("duration_within", 1.0),
                     "previous_center": model.centers.get("previous_gap", 0.0),
                     "previous_scale": model.scales.get("previous_gap", 1.0)}
        for endpoint in endpoints:
            mu = _model_mu(model, feature, float(endpoint), self.mark_mode)
            numerator, denominator = _conditional_node_loglik(evidence, float(endpoint), mu, model.sigma)
            log_num.append(numerator)
            log_den.append(denominator)
        return float(logsumexp(log_num) - logsumexp(log_den))


def _make_transform(rows: Sequence[Mapping[str, Any]], model_name: str, mark_mode: str,
                    endpoints: Mapping[int, np.ndarray]) -> dict[str, Any]:
    durations: list[float] = []
    previous: list[float] = []
    for row in rows:
        feature = row["feature"]
        endpoint = float(row["endpoints"][0])
        if model_name in ("M1", "M3"):
            duration = _duration_value(feature, endpoint, mark_mode)
            if duration is not None:
                durations.append(math.log(duration))
        if model_name in ("M2", "M3"):
            gap = _previous_value(feature)
            if gap is not None:
                previous.append(math.log(gap))
    transform: dict[str, Any] = {}
    if model_name in ("M1", "M3"):
        if mark_mode == "log_duration":
            center = float(np.mean(durations))
            scale = float(np.std(durations))
            if not math.isfinite(scale) or scale <= 1e-10:
                raise ValueError(f"{model_name} duration predictor is degenerate")
            transform.update(duration_center=center, duration_scale=scale)
        else:
            grouped = {"0": [v for v in durations if math.exp(v) < 12.0],
                       "1": [v for v in durations if math.exp(v) >= 12.0]}
            centers = {key: float(np.mean(value)) if value else 0.0 for key, value in grouped.items()}
            residuals = [v - centers["1" if math.exp(v) >= 12.0 else "0"] for v in durations]
            scale = float(np.std(residuals))
            if not math.isfinite(scale) or scale <= 1e-10:
                raise ValueError(f"{model_name} within-type duration predictor is degenerate")
            transform.update(duration_type_centers=centers, duration_within_scale=scale)
    if model_name in ("M2", "M3"):
        center = float(np.mean(previous))
        scale = float(np.std(previous))
        if not math.isfinite(scale) or scale <= 1e-10:
            raise ValueError(f"{model_name} previous-gap predictor is degenerate")
        transform.update(previous_center=center, previous_scale=scale)
    return transform


def _fit_model(model_name: str, rows: Sequence[Mapping[str, Any]], endpoint_mode: str,
               nodes: int, mark_mode: str, counts: Mapping[str, int]) -> ForecastModel:
    terms = _model_terms(model_name, mark_mode)
    if len(rows) < max(2, len(terms) + 2):
        raise ValueError(f"{model_name} has too few feature-available training rows")
    transform = _make_transform(rows, model_name, mark_mode, {r["feature"]["emission_index"]: r["endpoints"] for r in rows})
    starts = _initial_starts(rows, terms, transform, mark_mode)
    prepared = _prepare_likelihood(rows, terms, transform, mark_mode)

    results = [minimize(prepared.objective, start, method="L-BFGS-B",
                        bounds=(_BOUNDS[0],) + (_BOUNDS[1],) * len(terms) + (_BOUNDS[3],))
               for start in starts]
    best = _choose_result(results, model_name)
    if math.exp(float(best.x[-1])) <= math.exp(-4.0) + _EPS:
        raise ValueError(f"{model_name} fitted a degenerate residual scale")
    centers: dict[str, Any] = {}
    scales: dict[str, Any] = {}
    if "duration_center" in transform:
        centers["duration"] = transform["duration_center"]
        scales["duration"] = transform["duration_scale"]
    if "duration_type_centers" in transform:
        centers["duration_type"] = transform["duration_type_centers"]
        scales["duration_within"] = transform["duration_within_scale"]
    if "previous_center" in transform:
        centers["previous_gap"] = transform["previous_center"]
        scales["previous_gap"] = transform["previous_scale"]
    coefficients = {term: float(best.x[i + 1]) for i, term in enumerate(terms)}
    return ForecastModel(name=model_name, intercept=float(best.x[0]), coefficients=coefficients,
                         sigma=math.exp(float(best.x[-1])), centers=centers, scales=scales,
                         n_fit=len(rows), terms=terms,
                         metadata={"fit_kind": "conditional_landmark", "n_fit": len(rows),
                                   "counts": dict(counts), "convergence": _diagnostics(results, best,
                                                                                         (_BOUNDS[0],) + (_BOUNDS[1],) * len(terms) + (_BOUNDS[3],)),
                                   "fallback": {"M1": "M0", "M2": "M0", "M3": "M2/M1/M0"}.get(model_name)})


def fit_models(ledger: Sequence[Mapping[str, Any]], evidence: Sequence[Mapping[str, Any]],
               training_cutoff: float, *, endpoint_mode: str = "point", nodes: int = 5,
               mark_mode: str = "log_duration") -> ForecastBundle:
    """Fit frozen M0--M3 models and the shared issue-anchored R0 fallback."""
    cutoff = _as_float(training_cutoff, "training_cutoff")
    if endpoint_mode not in {"point", "uniform_end"}:
        raise ValueError("endpoint_mode must be 'point' or 'uniform_end'")
    if not isinstance(nodes, int) or nodes < 1:
        raise ValueError("nodes must be a positive integer")
    if mark_mode not in {"log_duration", "type_within"}:
        raise ValueError("mark_mode must be 'log_duration' or 'type_within'")
    features = _validate_features(ledger, cutoff)
    indexed_evidence = _validate_evidence(evidence, cutoff)
    if set(features) != set(indexed_evidence):
        raise ValueError("ledger and evidence must contain the same emission indices")
    counts = _counts(evidence)
    pairs = []
    for index in sorted(features):
        feature = features[index]
        ev = indexed_evidence[index]
        if ev["kind"] == "excluded":
            continue
        if float(ev["issue_time"]) != float(feature["issue_time"]):
            raise ValueError("feature and evidence issue_time do not match")
        endpoints = _endpoint_nodes(feature, endpoint_mode, nodes)
        if endpoints is not None:
            pairs.append({"feature": feature, "evidence": ev, "endpoints": endpoints})
    all_rows = [{"feature": features[i], "evidence": indexed_evidence[i], "endpoints": np.array([0.0]),
                 "model_name": "M0"} for i in sorted(features) if indexed_evidence[i]["kind"] != "excluded"]
    r0 = _fit_r0(all_rows, counts)
    models: dict[str, ForecastModel] = {}
    for model_name in _MODEL_NAMES:
        available = []
        for row in pairs:
            feature, endpoints = row["feature"], row["endpoints"]
            if model_name in ("M1", "M3") and not _duration_availability(feature, endpoints, mark_mode):
                continue
            if model_name in ("M2", "M3") and _previous_value(feature) is None:
                continue
            available.append(row)
        for row in available:
            row["model_name"] = model_name
        models[model_name] = _fit_model(model_name, available, endpoint_mode, nodes, mark_mode, counts)
    metadata = {"training_cutoff": cutoff, "frozen": True,
                "conditional_likelihood": "landmark survival with interval and right-censor terms",
                "uniform_end_sensitivity": "partial measurement sensitivity; onset_t and previous_gap held fixed"}
    return ForecastBundle(models=models, r0=r0, endpoint_mode=endpoint_mode, nodes=nodes,
                          mark_mode=mark_mode, counts=counts, metadata=metadata)
