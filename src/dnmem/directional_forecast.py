"""Fixed-baseline directional A10c forecast models.

This module keeps the A10b landmark likelihood and fits the A10c extensions in
stages: M0 and M2 are fitted once, then M3 and P3 only estimate a bounded mark
offset with the M2 parameters held fixed.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp

from dnmem.ledger_forecast import (
    ForecastModel,
    _BOUNDS,
    _EPS,
    _PreparedLikelihood,
    _as_float,
    _choose_result,
    _conditional_node_loglik,
    _counts,
    _diagnostics,
    _endpoint_nodes,
    _fit_r0,
    _log_interval_array,
    _log_survival_array,
    _previous_value,
    _remaining_loglik,
    _validate_evidence,
    _validate_features,
)


_NODES = 5
_MODEL_NAMES = ("M0", "M2", "M3", "P3")
_TERMS = ("previous_gap", "earlier_level")


def _positive(value: Any, label: str) -> float | None:
    if value is None:
        return None
    result = _as_float(value, label)
    if result <= 0.0:
        return None
    return result


def _earlier_level(feature: Mapping[str, Any]) -> float | None:
    values = feature.get("earlier_gaps")
    if values is None or values == []:
        return None
    if not isinstance(values, (list, tuple)):
        raise ValueError("feature.earlier_gaps must be a list")
    finite = [_as_float(value, "feature.earlier_gaps") for value in values]
    if not finite:
        return None
    return float(np.mean(finite))


def _standard(values: Sequence[float]) -> tuple[float, float, bool]:
    if not values:
        return 0.0, 1.0, True
    center = float(np.mean(values)) if values else 0.0
    scale = float(np.std(values)) if values else 1.0
    fixed = not math.isfinite(scale) or scale <= 1e-10
    return center, (1.0 if fixed else scale), fixed


def _m2_transform(rows: Sequence[Mapping[str, Any]], local_level: bool) -> tuple[dict[str, Any], list[str]]:
    previous = [_as_float(_previous_value(row["feature"]), "feature.previous_gap") for row in rows]
    q_center, q_scale, q_fixed = _standard([math.log(value) for value in previous])
    transform: dict[str, Any] = {"previous_center": q_center, "previous_scale": q_scale}
    fixed = ["previous_gap"] if q_fixed else []
    if local_level:
        levels = [_earlier_level(row["feature"]) for row in rows]
        observed = [value for value in levels if value is not None]
        l_center, l_scale, l_fixed = _standard(observed)
        transform.update(earlier_center=l_center, earlier_scale=l_scale)
        if l_fixed:
            fixed.append("earlier_level")
    return transform, fixed


def _m2_covariates(feature: Mapping[str, Any], transform: Mapping[str, Any],
                  local_level: bool) -> dict[str, float]:
    previous = _previous_value(feature)
    if previous is None:
        raise ValueError("previous gap is unavailable")
    values = {"previous_gap": (math.log(previous) - float(transform["previous_center"]))
              / float(transform["previous_scale"])}
    if local_level:
        level = _earlier_level(feature)
        values["earlier_level"] = (0.0 if level is None else
                                    (level - float(transform["earlier_center"]))
                                    / float(transform["earlier_scale"]))
    return values


def _response_starts(rows: Sequence[Mapping[str, Any]], n_terms: int) -> list[np.ndarray]:
    values = []
    for row in rows:
        evidence = row["evidence"]
        issue = float(evidence["issue_time"])
        if evidence["kind"] == "interval":
            lo = float(evidence["onset_lo"]) - issue
            hi = float(evidence["onset_hi"]) - issue
            if lo >= 0.0 and hi > lo:
                values.append(math.log((lo + hi) / 2.0))
        else:
            censor = float(evidence["censor_at"]) - issue
            if censor > 0.0:
                values.append(math.log(censor))
    if not values:
        values = [0.0]
    scale = max(0.25, min(2.0, float(np.std(values)) or 0.5))
    return [np.array([float(np.mean(values)), *([0.0] * n_terms), math.log(scale)]),
            np.array([float(np.median(values)), *([0.0] * n_terms), math.log(max(0.25, scale * 0.8))])]


def _choose_conditional_result(results: Sequence[Any], name: str,
                               fixed_terms: Sequence[str], terms: Sequence[str]) -> Any:
    successful = [result for result in results if bool(result.success)
                  and np.all(np.isfinite(result.x)) and math.isfinite(float(result.fun))
                  and float(result.fun) < 1e99]
    if not successful:
        messages = "; ".join(str(result.message) for result in results)
        raise ValueError(f"{name} optimization failed: {messages}")
    best = min(successful, key=lambda result: float(result.fun))
    fixed_positions = {1 + terms.index(term) for term in fixed_terms}
    gradient = np.asarray(best.jac, dtype=float) if best.jac is not None else np.array([])
    if (len(gradient) != len(best.x)
            or any(not math.isfinite(float(value)) for i, value in enumerate(gradient)
                   if i not in fixed_positions)):
        raise ValueError(f"{name} optimization returned a non-finite gradient")
    return best


def _prepare_directional(rows: Sequence[Mapping[str, Any]], terms: tuple[str, ...],
                         transform: Mapping[str, Any], local_level: bool) -> _PreparedLikelihood:
    n_rows = len(rows)
    n_nodes = max(len(row["endpoints"]) for row in rows)
    design = np.zeros((n_rows, n_nodes, len(terms)), dtype=float)
    lower = np.zeros((n_rows, n_nodes), dtype=float)
    upper = np.ones((n_rows, n_nodes), dtype=float)
    censor = np.zeros((n_rows, n_nodes), dtype=float)
    age = np.zeros((n_rows, n_nodes), dtype=float)
    weights = np.full((n_rows, n_nodes), -math.inf, dtype=float)
    is_interval = np.zeros(n_rows, dtype=bool)
    for i, row in enumerate(rows):
        feature, evidence, endpoints = row["feature"], row["evidence"], row["endpoints"]
        issue = float(evidence["issue_time"])
        is_interval[i] = evidence["kind"] == "interval"
        weights[i, :len(endpoints)] = -math.log(len(endpoints))
        covariates = _m2_covariates(feature, transform, local_level) if terms else {}
        for j, endpoint in enumerate(endpoints):
            endpoint = float(endpoint)
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
    return _PreparedLikelihood(design, lower, upper, censor, age, is_interval, weights)


def _fit_conditional(name: str, rows: Sequence[Mapping[str, Any]], terms: tuple[str, ...],
                     transform: Mapping[str, Any], local_level: bool,
                     fixed_terms: Sequence[str] = ()) -> ForecastModel:
    if len(rows) < max(2, len(terms) + 2):
        raise ValueError(f"{name} has too few feature-available training rows")
    prepared = _prepare_directional(rows, terms, transform, local_level)
    bounds = [_BOUNDS[0]] + [(0.0, 0.0) if term in fixed_terms else _BOUNDS[1]
                             for term in terms] + [_BOUNDS[3]]
    starts = _response_starts(rows, len(terms))
    results = [minimize(prepared.objective, start, method="L-BFGS-B", bounds=bounds)
               for start in starts]
    best = _choose_conditional_result(results, name, fixed_terms, terms)
    if math.exp(float(best.x[-1])) <= math.exp(_BOUNDS[3][0]) + _EPS:
        raise ValueError(f"{name} fitted a degenerate residual scale")
    coefficients = {term: float(best.x[i + 1]) for i, term in enumerate(terms)}
    centers: dict[str, Any] = {}
    scales: dict[str, Any] = {}
    if "previous_gap" in terms:
        centers["previous_gap"], scales["previous_gap"] = transform["previous_center"], transform["previous_scale"]
    if "earlier_level" in terms:
        centers["earlier_level"], scales["earlier_level"] = transform["earlier_center"], transform["earlier_scale"]
    convergence = _diagnostics(results, best, bounds)
    convergence["gradient_finite_free"] = True
    return ForecastModel(
        name=name, intercept=float(best.x[0]), coefficients=coefficients,
        sigma=math.exp(float(best.x[-1])), centers=centers, scales=scales,
        n_fit=len(rows), terms=terms,
        metadata={"fit_kind": "conditional_landmark", "n_fit": len(rows),
                  "fixed_terms": list(fixed_terms),
                  "convergence": convergence},
    )


def _mark_duration(feature: Mapping[str, Any], endpoint: float, kind: str) -> float | None:
    if kind == "previous":
        return _positive(feature.get("previous_duration"), "feature.previous_duration")
    onset = feature.get("onset_t")
    if onset is not None:
        duration = endpoint - _as_float(onset, "feature.onset_t")
    else:
        duration = feature.get("duration")
        duration = None if duration is None else _as_float(duration, "feature.duration")
    return None if duration is None or duration <= 0.0 else duration


def _mark_components(duration: float, mark_mode: str, transform: Mapping[str, Any]) -> np.ndarray:
    log_duration = math.log(duration)
    if mark_mode == "log_duration":
        return np.array([(log_duration - float(transform["mark_center"])) /
                         float(transform["mark_scale"])])
    kind = float(duration >= 12.0)
    key = str(int(kind))
    within = ((log_duration - float(transform["type_centers"][key])) /
              float(transform["within_scale"]))
    return np.array([kind, within])


def _mark_transform(rows: Sequence[Mapping[str, Any]], kind: str, mark_mode: str,
                    endpoint_mode: str, allowed_indices: Sequence[int] | None = None) -> tuple[dict[str, Any], list[int]]:
    values: list[float] = []
    valid_indices: list[int] = []
    by_type: dict[str, list[float]] = {"0": [], "1": []}
    candidates = range(len(rows)) if allowed_indices is None else allowed_indices
    for i in candidates:
        row = rows[i]
        durations = [_mark_duration(row["feature"], float(endpoint), kind)
                     for endpoint in row["endpoints"]]
        if not durations or any(value is None for value in durations):
            continue
        valid_indices.append(i)
        values.extend(float(value) for value in durations)
    if mark_mode == "log_duration":
        logs = [math.log(value) for value in values]
        center, scale, fixed = _standard(logs)
        return {"mark_center": center, "mark_scale": scale, "mark_fixed": [0] if fixed else []}, valid_indices
    logs = [math.log(value) for value in values]
    for value in logs:
        by_type[str(int(math.exp(value) >= 12.0))].append(value)
    type_centers = {key: (float(np.mean(value)) if value else 0.0) for key, value in by_type.items()}
    residuals = [value - type_centers[str(int(math.exp(value) >= 12.0))] for value in logs]
    _, within_scale, within_fixed = _standard(residuals)
    type_fixed = [0] if not by_type["0"] or not by_type["1"] else []
    return {"type_centers": type_centers, "within_scale": within_scale,
            "mark_fixed": type_fixed + ([1] if within_fixed else [])}, valid_indices


def _offset_objective(beta: np.ndarray, rows: Sequence[Mapping[str, Any]], base: ForecastModel,
                      base_transform: Mapping[str, Any], mark_transform: Mapping[str, Any],
                      mark_kind: str, mark_mode: str, local_level: bool) -> float:
    log_likelihood = 0.0
    for row in rows:
        feature, evidence, endpoints = row["feature"], row["evidence"], row["endpoints"]
        covariates = _m2_covariates(feature, base_transform, local_level)
        numerators, denominators = [], []
        for endpoint in endpoints:
            mark = _mark_duration(feature, float(endpoint), mark_kind)
            offset = 0.0 if mark is None else float(np.dot(beta, _mark_components(mark, mark_mode, mark_transform)))
            mu = base.intercept + sum(base.coefficients[name] * covariates[name] for name in base.terms) + offset
            numerator, denominator = _conditional_node_loglik(evidence, float(endpoint), mu, base.sigma)
            numerators.append(numerator)
            denominators.append(denominator)
        log_likelihood += float(np.logaddexp.reduce(numerators) - np.logaddexp.reduce(denominators))
    value = -log_likelihood
    return value if math.isfinite(value) else 1e100


@dataclass(frozen=True)
class _PreparedOffset:
    base_mu: np.ndarray
    marks: np.ndarray
    interval_lower: np.ndarray
    interval_upper: np.ndarray
    censor_time: np.ndarray
    age: np.ndarray
    is_interval: np.ndarray
    node_log_weights: np.ndarray
    sigma: float

    def objective(self, beta: np.ndarray) -> float:
        mu = self.base_mu + np.einsum("nkp,p->nk", self.marks, beta)
        numerator_interval = _log_interval_array(self.interval_lower, self.interval_upper, mu, self.sigma)
        numerator_censored = _log_survival_array(self.censor_time, mu, self.sigma)
        numerator_censored = np.where(self.censor_time <= _EPS, 0.0, numerator_censored)
        numerator = np.where(self.is_interval[:, None], numerator_interval, numerator_censored)
        denominator = _log_survival_array(self.age, mu, self.sigma)
        value = -float(np.sum(logsumexp(numerator + self.node_log_weights, axis=1)
                              - logsumexp(denominator + self.node_log_weights, axis=1)))
        return value if math.isfinite(value) else 1e100


def _prepare_offset(rows: Sequence[Mapping[str, Any]], base: ForecastModel,
                    base_transform: Mapping[str, Any], mark_transform: Mapping[str, Any],
                    mark_kind: str, mark_mode: str, local_level: bool) -> _PreparedOffset:
    n_rows = len(rows)
    n_nodes = max(len(row["endpoints"]) for row in rows)
    n_beta = 1 if mark_mode == "log_duration" else 2
    base_mu = np.zeros((n_rows, n_nodes), dtype=float)
    marks = np.zeros((n_rows, n_nodes, n_beta), dtype=float)
    lower = np.zeros((n_rows, n_nodes), dtype=float)
    upper = np.ones((n_rows, n_nodes), dtype=float)
    censor = np.zeros((n_rows, n_nodes), dtype=float)
    age = np.zeros((n_rows, n_nodes), dtype=float)
    weights = np.full((n_rows, n_nodes), -math.inf, dtype=float)
    is_interval = np.zeros(n_rows, dtype=bool)
    for i, row in enumerate(rows):
        feature, evidence, endpoints = row["feature"], row["evidence"], row["endpoints"]
        issue = float(evidence["issue_time"])
        covariates = _m2_covariates(feature, base_transform, local_level)
        base_value = base.intercept + sum(base.coefficients[name] * covariates[name] for name in base.terms)
        is_interval[i] = evidence["kind"] == "interval"
        weights[i, :len(endpoints)] = -math.log(len(endpoints))
        for j, endpoint in enumerate(endpoints):
            endpoint = float(endpoint)
            base_mu[i, j] = base_value
            duration = _mark_duration(feature, endpoint, mark_kind)
            if duration is None:
                raise ValueError("offset preparation requires valid marks")
            marks[i, j, :] = _mark_components(duration, mark_mode, mark_transform)
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
    return _PreparedOffset(base_mu, marks, lower, upper, censor, age, is_interval,
                           weights, base.sigma)


def _fit_offset(name: str, rows: Sequence[Mapping[str, Any]], base: ForecastModel,
                base_transform: Mapping[str, Any], mark_kind: str, mark_mode: str,
                local_level: bool, directional: bool, joint_marks: bool) -> ForecastModel:
    def valid_for(kind: str) -> list[int]:
        valid = []
        for i, row in enumerate(rows):
            if all(_mark_duration(row["feature"], float(endpoint), kind) is not None
                   for endpoint in row["endpoints"]):
                valid.append(i)
        return valid

    common_indices = set(valid_for("current")) & set(valid_for("previous")) if joint_marks else None
    allowed = sorted(common_indices) if common_indices is not None else valid_for(mark_kind)
    mark_transform, valid_indices = _mark_transform(rows, mark_kind, mark_mode, "point", allowed)
    if joint_marks:
        valid_indices = [i for i in valid_indices if i in common_indices]
    offset_rows = [rows[i] for i in valid_indices]
    n_beta = 1 if mark_mode == "log_duration" else 2
    fixed_indices = set(mark_transform.get("mark_fixed", []))
    fixed = len(fixed_indices) == n_beta
    bounds = [(0.0, 0.0) if i in fixed_indices else ((0.0, 5.0) if directional else (-5.0, 5.0))
              for i in range(n_beta)]
    zero = np.zeros(n_beta, dtype=float)
    candidates: list[tuple[np.ndarray, Any]] = [(zero, None)]
    starts = []
    for value in (0.1, 1.0):
        start = np.full(n_beta, value, dtype=float)
        for index in fixed_indices:
            start[index] = 0.0
        starts.append(start)
    failures: list[dict[str, Any]] = []
    successful: list[dict[str, Any]] = []
    prepared = _prepare_offset(offset_rows, base, base_transform, mark_transform,
                               mark_kind, mark_mode, local_level) if offset_rows else None
    if not fixed and offset_rows:
        for start in starts:
            result = minimize(prepared.objective, start, method="L-BFGS-B", bounds=bounds)
            free = [i for i in range(len(result.x)) if i not in fixed_indices]
            gradient = np.asarray(result.jac, dtype=float) if result.jac is not None else np.array([])
            valid_result = (bool(result.success) and np.all(np.isfinite(result.x))
                            and math.isfinite(float(result.fun)) and float(result.fun) < 1e99
                            and len(gradient) == len(result.x)
                            and all(math.isfinite(float(gradient[i])) for i in free))
            if valid_result:
                candidates.append((np.asarray(result.x, dtype=float), result))
                successful.append({"start": start.tolist(), "objective": float(result.fun),
                                   "message": str(result.message)})
            else:
                failures.append({"start": start.tolist(), "success": bool(result.success),
                                 "message": str(result.message), "objective": float(result.fun)
                                 if math.isfinite(float(result.fun)) else None})
    zero_value = prepared.objective(zero) if prepared is not None else 0.0
    candidates[0] = (zero, type("Candidate", (), {"fun": zero_value})())
    if not fixed and offset_rows and not successful:
        raise ValueError(f"{name} offset optimization failed: no valid starts; {failures}")
    beta, result = min(candidates, key=lambda item: float(item[1].fun))
    beta = np.asarray(beta, dtype=float)
    optimized = bool(successful)
    beta_names = ["beta"] if n_beta == 1 else ["beta_type", "beta_within"]
    coefficients = dict(base.coefficients)
    coefficients.update({key: float(value) for key, value in zip(beta_names, beta)})
    centers = dict(base.centers)
    scales = dict(base.scales)
    if mark_mode == "log_duration":
        centers["mark"] = mark_transform["mark_center"]
        scales["mark"] = mark_transform["mark_scale"]
    else:
        centers["mark_type"] = mark_transform["type_centers"]
        scales["mark_within"] = mark_transform["within_scale"]
    at_bound = any(abs(float(value) - bounds[i][0]) <= 1e-7 for i, value in enumerate(beta))
    return ForecastModel(
        name=name, intercept=base.intercept, coefficients=coefficients, sigma=base.sigma,
        centers=centers, scales=scales, n_fit=len(rows),
        terms=base.terms + tuple(beta_names),
        metadata={"fit_kind": "fixed_m2_mark_offset", "base_model": "M2",
                  "mark_kind": mark_kind, "mark_mode": mark_mode,
                  "directional": directional, "joint_marks": joint_marks,
                  "beta": beta.tolist(), "at_bound": at_bound,
                  "fit_status": "optimized" if optimized else "zero_candidate",
                  "unidentifiable": fixed or not valid_indices,
                  "fixed_beta_indices": sorted(fixed_indices),
                  "valid_mark_count": len(valid_indices), "n_fit": len(offset_rows),
                  "baseline_training_count": len(rows), "successful_starts": successful,
                  "failed_starts": failures, "selected_zero_objective": zero_value},
    )


def _model_from_dict(payload: Mapping[str, Any]) -> ForecastModel:
    return ForecastModel(name=str(payload["name"]), intercept=float(payload["intercept"]),
                         coefficients={str(k): float(v) for k, v in payload["coefficients"].items()},
                         sigma=float(payload["sigma"]), centers=dict(payload.get("centers", {})),
                         scales=dict(payload.get("scales", {})), n_fit=int(payload["n_fit"]),
                         terms=tuple(payload.get("terms", ())), metadata=dict(payload.get("metadata", {})))


def _feature_mark(feature: Mapping[str, Any], endpoints: np.ndarray, kind: str,
                  mark_mode: str, transform: Mapping[str, Any]) -> np.ndarray | None:
    durations = [_mark_duration(feature, float(endpoint), kind) for endpoint in endpoints]
    if not durations or any(value is None for value in durations):
        return None
    return np.asarray([_mark_components(float(value), mark_mode, transform) for value in durations])


@dataclass(frozen=True)
class DirectionalBundle:
    models: dict[str, ForecastModel]
    r0: ForecastModel
    endpoint_mode: str
    nodes: int
    mark_mode: str
    local_level: bool
    directional: bool
    joint_marks: bool
    counts: dict[str, int]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"models": {name: model.to_dict() for name, model in self.models.items()},
                "r0": self.r0.to_dict(), "endpoint_mode": self.endpoint_mode,
                "nodes": self.nodes, "mark_mode": self.mark_mode,
                "local_level": self.local_level, "directional": self.directional,
                "joint_marks": self.joint_marks, "counts": dict(self.counts),
                "metadata": dict(self.metadata)}

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "DirectionalBundle":
        models = {name: _model_from_dict(value) for name, value in payload["models"].items()}
        return cls(models=models, r0=_model_from_dict(payload["r0"]),
                   endpoint_mode=str(payload["endpoint_mode"]), nodes=int(payload["nodes"]),
                   mark_mode=str(payload["mark_mode"]), local_level=bool(payload["local_level"]),
                   directional=bool(payload["directional"]), joint_marks=bool(payload["joint_marks"]),
                   counts={str(k): int(v) for k, v in payload["counts"].items()},
                   metadata=dict(payload.get("metadata", {})))

    def _base_transform(self) -> dict[str, Any]:
        result = {"previous_center": self.models["M2"].centers.get("previous_gap", 0.0),
                  "previous_scale": self.models["M2"].scales.get("previous_gap", 1.0)}
        if self.local_level:
            result.update(earlier_center=self.models["M2"].centers.get("earlier_level", 0.0),
                          earlier_scale=self.models["M2"].scales.get("earlier_level", 1.0))
        return result

    def _mark_transform(self, model: ForecastModel) -> dict[str, Any]:
        if self.mark_mode == "log_duration":
            return {"mark_center": model.centers.get("mark", 0.0),
                    "mark_scale": model.scales.get("mark", 1.0)}
        return {"type_centers": model.centers.get("mark_type", {"0": 0.0, "1": 0.0}),
                "within_scale": model.scales.get("mark_within", 1.0)}

    def route(self, feature: Mapping[str, Any], model_name: str) -> str:
        if model_name not in _MODEL_NAMES:
            raise ValueError(f"unknown model {model_name!r}")
        endpoints = _endpoint_nodes(feature, self.endpoint_mode, self.nodes)
        if endpoints is None:
            return "R0"
        previous_ok = _previous_value(feature) is not None
        if model_name == "M0":
            return "M0"
        if not previous_ok:
            return "M0"
        if model_name == "M2":
            return "M2"
        model = self.models[model_name]
        beta_keys = ("beta",) if self.mark_mode == "log_duration" else ("beta_type", "beta_within")
        if all(float(model.coefficients.get(key, 0.0)) == 0.0 for key in beta_keys):
            return "M2"
        mark_kind = "current" if model_name == "M3" else "previous"
        if _feature_mark(feature, endpoints, mark_kind, self.mark_mode, self._mark_transform(model)) is None:
            return "M2"
        return model_name

    def _score_selected(self, feature: Mapping[str, Any], evidence: Mapping[str, Any],
                        selected: str, endpoints: np.ndarray) -> float:
        if selected == "R0":
            return float(_remaining_loglik(evidence, self.r0.intercept, self.r0.sigma))
        model = self.models[selected]
        base = self.models["M2"] if selected in ("M2", "M3", "P3") else model
        base_transform = self._base_transform()
        mark = None
        if selected in ("M3", "P3"):
            mark = _feature_mark(feature, endpoints, "current" if selected == "M3" else "previous",
                                 self.mark_mode, self._mark_transform(model))
        covariates = {} if selected == "M0" else _m2_covariates(feature, base_transform, self.local_level)
        beta_keys = ("beta",) if self.mark_mode == "log_duration" else ("beta_type", "beta_within")
        log_num, log_den = [], []
        for j, endpoint in enumerate(endpoints):
            mu = model.intercept if selected == "M0" else base.intercept + sum(
                base.coefficients[name] * covariates[name] for name in base.terms)
            if mark is not None:
                mu += sum(model.coefficients[key] * float(value)
                          for key, value in zip(beta_keys, mark[j]))
            numerator, denominator = _conditional_node_loglik(evidence, float(endpoint), mu, model.sigma)
            log_num.append(numerator)
            log_den.append(denominator)
        return float(np.logaddexp.reduce(log_num) - np.logaddexp.reduce(log_den))

    def score(self, feature: Mapping[str, Any], evidence: Mapping[str, Any], model_name: str) -> float | None:
        if evidence.get("kind") == "excluded":
            return None
        if int(feature["emission_index"]) != int(evidence["emission_index"]):
            raise ValueError("feature and evidence emission_index do not match")
        if float(feature["issue_time"]) != float(evidence["issue_time"]):
            raise ValueError("feature and evidence issue_time do not match")
        endpoints = _endpoint_nodes(feature, self.endpoint_mode, self.nodes)
        selected = self.route(feature, model_name)
        return self._score_selected(feature, evidence, selected, endpoints if endpoints is not None else np.array([0.0]))

    def batchscore(self, ledger: Sequence[Mapping[str, Any]],
                   evidence: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
        def index_rows(rows: Sequence[Mapping[str, Any]], label: str) -> dict[int, Mapping[str, Any]]:
            indexed: dict[int, Mapping[str, Any]] = {}
            for row in rows:
                index = int(row["emission_index"])
                if index in indexed:
                    raise ValueError(f"duplicate {label} emission_index {index}")
                indexed[index] = row
            return indexed

        features = index_rows(ledger, "feature")
        outcomes = index_rows(evidence, "evidence")
        if set(features) != set(outcomes):
            raise ValueError("ledger and evidence must contain the same emission indices")
        result = []
        for index in sorted(features):
            feature, outcome = features[index], outcomes[index]
            row: dict[str, Any] = {"emission_index": index,
                                   "issue_time": feature.get("issue_time"),
                                   "kind": outcome.get("kind"),
                                   "reason": outcome.get("reason")}
            if float(feature["issue_time"]) != float(outcome["issue_time"]):
                raise ValueError("feature and evidence issue_time do not match")
            if outcome.get("kind") == "excluded":
                for name in _MODEL_NAMES:
                    row[name], row[f"{name}_route"] = None, None
                row.update(gain_M3_M2=None, gain_P3_M2=None, gain_M3_P3=None)
                result.append(row)
                continue
            endpoints = _endpoint_nodes(feature, self.endpoint_mode, self.nodes)
            for name in _MODEL_NAMES:
                route = self.route(feature, name)
                row[name] = self._score_selected(feature, outcome, route,
                                                 endpoints if endpoints is not None else np.array([0.0]))
                row[f"{name}_route"] = route
            row["gain_M3_M2"] = row["M3"] - row["M2"]
            row["gain_P3_M2"] = row["P3"] - row["M2"]
            row["gain_M3_P3"] = row["M3"] - row["P3"]
            result.append(row)
        return result

    def scores(self, ledger: Sequence[Mapping[str, Any]], evidence: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
        return self.batchscore(ledger, evidence)


def fit_directional(ledger: Sequence[Mapping[str, Any]], evidence: Sequence[Mapping[str, Any]],
                    training_cutoff: float, *, endpoint_mode: str = "point",
                    local_level: bool = True, mark_mode: str = "log_duration",
                    directional: bool = True, joint_marks: bool = False) -> DirectionalBundle:
    cutoff = _as_float(training_cutoff, "training_cutoff")
    if endpoint_mode not in {"point", "uniform_end"}:
        raise ValueError("endpoint_mode must be 'point' or 'uniform_end'")
    if mark_mode not in {"log_duration", "type_within"}:
        raise ValueError("mark_mode must be 'log_duration' or 'type_within'")
    features = _validate_features(ledger, cutoff)
    outcomes = _validate_evidence(evidence, cutoff)
    if set(features) != set(outcomes):
        raise ValueError("ledger and evidence must contain the same emission indices")
    counts = _counts(evidence)
    known, all_rows = [], []
    for index in sorted(features):
        feature, outcome = features[index], outcomes[index]
        if outcome["kind"] == "excluded":
            continue
        if float(feature["issue_time"]) != float(outcome["issue_time"]):
            raise ValueError("feature and evidence issue_time do not match")
        all_rows.append({"feature": feature, "evidence": outcome, "endpoints": np.array([0.0]), "model_name": "R0"})
        endpoints = _endpoint_nodes(feature, endpoint_mode, _NODES)
        if endpoints is not None:
            known.append({"feature": feature, "evidence": outcome, "endpoints": endpoints, "model_name": "M0"})
    r0 = _fit_r0(all_rows, counts)
    m0 = _fit_conditional("M0", known, (), {}, False)
    q_rows = [row for row in known if _previous_value(row["feature"]) is not None]
    if not q_rows:
        raise ValueError("M2 has no covered positive previous-gap training rows")
    transform, fixed_terms = _m2_transform(q_rows, local_level)
    m2 = _fit_conditional("M2", q_rows, tuple(term for term in _TERMS if local_level or term != "earlier_level"),
                          transform, local_level, fixed_terms)
    m2.metadata["baseline_training_count"] = len(q_rows)
    m3 = _fit_offset("M3", q_rows, m2, transform, "current", mark_mode,
                     local_level, directional, joint_marks)
    p3 = _fit_offset("P3", q_rows, m2, transform, "previous", mark_mode,
                     local_level, directional, joint_marks)
    metadata = {"training_cutoff": cutoff, "frozen": True,
                "conditional_likelihood": "landmark survival with interval and right-censor terms",
                "base_model": "M2 fixed for M3/P3 offsets", "joint_marks": joint_marks}
    return DirectionalBundle(models={"M0": m0, "M2": m2, "M3": m3, "P3": p3}, r0=r0,
                             endpoint_mode=endpoint_mode, nodes=_NODES, mark_mode=mark_mode,
                             local_level=local_level, directional=directional,
                             joint_marks=joint_marks, counts=counts, metadata=metadata)


__all__ = ["DirectionalBundle", "fit_directional"]
