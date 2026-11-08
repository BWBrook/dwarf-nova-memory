"""Likelihood-support profiles for a frozen directional forecast bundle.

These diagnostics reproduce the fitted row populations and transforms.  Mark
profiles retain the staged estimator: M2 is fixed exactly while the mark
coefficient, or the other mark coefficient, is optimized conditionally.
"""

from __future__ import annotations

import copy
import math
from typing import Any, Callable, Mapping, Sequence

import numpy as np
from scipy.optimize import minimize

from .directional_forecast import (
    DirectionalBundle,
    _mark_duration,
    _offset_objective,
    _prepare_directional,
    _prepare_offset,
)
from .ledger_forecast import (
    _BOUNDS,
    _EPS,
    _conditional_node_loglik,
    _endpoint_nodes,
    _prepare_remaining,
    _previous_value,
    _r0_objective,
    _validate_evidence,
    _validate_features,
)


_LR_CUTOFF = 3.841
_DELTA_NLL = _LR_CUTOFF / 2.0
_BOUND_TOL = 1e-8


def _finite_float(value: Any, label: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def _bundle(value: DirectionalBundle | Mapping[str, Any]) -> DirectionalBundle:
    if isinstance(value, DirectionalBundle):
        return value
    if isinstance(value, Mapping):
        return DirectionalBundle.from_dict(value)
    raise TypeError("bundle must be a DirectionalBundle or serialized mapping")


def _rows(bundle: DirectionalBundle, ledger: Sequence[Mapping[str, Any]],
          evidence: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, Any]],
                                                          list[dict[str, Any]],
                                                          list[dict[str, Any]]]:
    cutoff = _finite_float(bundle.metadata.get("training_cutoff"), "bundle training_cutoff")
    features = _validate_features(ledger, cutoff)
    outcomes = _validate_evidence(evidence, cutoff)
    if set(features) != set(outcomes):
        raise ValueError("ledger and evidence must contain the same emission indices")
    remaining: list[dict[str, Any]] = []
    known: list[dict[str, Any]] = []
    for index in sorted(features):
        feature, outcome = features[index], outcomes[index]
        if outcome["kind"] == "excluded":
            continue
        if float(feature["issue_time"]) != float(outcome["issue_time"]):
            raise ValueError("feature and evidence issue_time do not match")
        remaining.append({"feature": feature, "evidence": outcome,
                          "endpoints": np.array([0.0]), "model_name": "R0"})
        endpoints = _endpoint_nodes(feature, bundle.endpoint_mode, bundle.nodes)
        if endpoints is not None:
            known.append({"feature": feature, "evidence": outcome,
                          "endpoints": endpoints, "model_name": "M0"})
    q_rows = [row for row in known if _previous_value(row["feature"]) is not None]
    expected = {"R0": bundle.r0.n_fit, "M0": bundle.models["M0"].n_fit,
                "M2": bundle.models["M2"].n_fit}
    observed = {"R0": len(remaining), "M0": len(known), "M2": len(q_rows)}
    if observed != expected:
        raise ValueError(f"profile row populations do not match frozen fit: {observed} != {expected}")
    return remaining, known, q_rows


def _conditional_scalar(rows: Sequence[Mapping[str, Any]], theta: np.ndarray,
                        terms: tuple[str, ...], bundle: DirectionalBundle) -> float:
    transform = bundle._base_transform()
    total = 0.0
    for row in rows:
        feature, outcome = row["feature"], row["evidence"]
        covariates = {} if not terms else {
            "previous_gap": (math.log(float(_previous_value(feature)))
                             - float(transform["previous_center"]))
                            / float(transform["previous_scale"])
        }
        if "earlier_level" in terms:
            values = feature.get("earlier_gaps")
            level = None if values is None or len(values) == 0 else float(np.mean(
                [_finite_float(value, "feature.earlier_gaps") for value in values]))
            covariates["earlier_level"] = (0.0 if level is None else
                                            (level - float(transform["earlier_center"]))
                                            / float(transform["earlier_scale"]))
        numerators, denominators = [], []
        for endpoint in row["endpoints"]:
            mu = float(theta[0]) + sum(float(theta[i + 1]) * covariates[term]
                                       for i, term in enumerate(terms))
            numerator, denominator = _conditional_node_loglik(
                outcome, float(endpoint), mu, math.exp(float(theta[-1])))
            numerators.append(numerator)
            denominators.append(denominator)
        total += float(np.logaddexp.reduce(numerators) - np.logaddexp.reduce(denominators))
    value = -total
    return value if math.isfinite(value) else 1e100


class _Profiler:
    def __init__(self, objective: Callable[[np.ndarray], float], fitted: Sequence[float],
                 bounds: Sequence[tuple[float, float]], names: Sequence[str],
                 fixed: Mapping[int, str] | None = None):
        self.objective = objective
        self.fitted = np.asarray(fitted, dtype=float)
        self.bounds = tuple((float(lo), float(hi)) for lo, hi in bounds)
        self.names = tuple(names)
        self.fixed = dict(fixed or {})
        if len(self.fitted) != len(self.bounds) or len(self.names) != len(self.bounds):
            raise ValueError("profile parameter dimensions do not agree")
        if any(not lo <= value <= hi for value, (lo, hi) in zip(self.fitted, self.bounds)):
            raise ValueError("frozen parameter lies outside its declared bounds")
        self.frozen_objective = _finite_float(self.objective(self.fitted), "frozen objective")
        if self.frozen_objective >= 1e99:
            raise ValueError("frozen likelihood is invalid")
        self.material_tolerance = max(1e-7, 1e-6 * (1.0 + abs(self.frozen_objective)))
        self.full_optimum_objective = self.frozen_objective
        self.full_optimizer_message = "no free parameters"
        self._check_full_optimum()

    def _check_result(self, result: Any, free_count: int, label: str) -> None:
        if (not bool(result.success) or not np.all(np.isfinite(result.x))
                or not math.isfinite(float(result.fun)) or float(result.fun) >= 1e99):
            raise ValueError(f"{label} constrained optimization failed: {result.message}")
        gradient = np.asarray(result.jac, dtype=float) if result.jac is not None else np.array([])
        if len(gradient) != free_count or not np.all(np.isfinite(gradient)):
            raise ValueError(f"{label} constrained optimization returned a nonfinite gradient")

    def _check_better(self, objective: float, label: str) -> None:
        improvement = self.frozen_objective - objective
        if improvement > self.material_tolerance:
            raise ValueError(
                f"{label} profile optimum is materially better than frozen fit "
                f"({improvement:.8g} NLL)"
            )

    def _check_full_optimum(self) -> None:
        free = [i for i, (lo, hi) in enumerate(self.bounds) if hi > lo]
        if not free:
            return

        def reduced(values: np.ndarray) -> float:
            theta = self.fitted.copy()
            theta[free] = values
            return self.objective(theta)

        result = minimize(reduced, self.fitted[free], method="L-BFGS-B",
                          bounds=[self.bounds[i] for i in free])
        self._check_result(result, len(free), "full")
        self.full_optimum_objective = float(result.fun)
        self.full_optimizer_message = str(result.message)
        self._check_better(float(result.fun), "full")

    def diagnostics(self) -> dict[str, Any]:
        return {
            "frozen_objective": self.frozen_objective,
            "full_reoptimization_objective": self.full_optimum_objective,
            "full_reoptimization_improvement": self.frozen_objective - self.full_optimum_objective,
            "material_improvement_tolerance": self.material_tolerance,
            "full_optimizer_message": self.full_optimizer_message,
        }

    def _evaluate(self, index: int, value: float) -> dict[str, Any]:
        lo, hi = self.bounds[index]
        value = min(hi, max(lo, float(value)))
        free = [i for i, (lower, upper) in enumerate(self.bounds)
                if i != index and upper > lower]
        theta = self.fitted.copy()
        theta[index] = value
        if free:
            def reduced(values: np.ndarray) -> float:
                candidate = theta.copy()
                candidate[free] = values
                return self.objective(candidate)

            result = minimize(reduced, theta[free], method="L-BFGS-B",
                              bounds=[self.bounds[i] for i in free])
            self._check_result(result, len(free), self.names[index])
            theta[free] = result.x
            objective = float(result.fun)
            message = str(result.message)
        else:
            objective = _finite_float(self.objective(theta), self.names[index] + " objective")
            if objective >= 1e99:
                raise ValueError(f"{self.names[index]} constrained likelihood is invalid")
            message = "no free nuisance parameters"
        self._check_better(objective, self.names[index])
        raw_lr = 2.0 * (objective - self.frozen_objective)
        likelihood_ratio = max(0.0, raw_lr)
        return {"value": value, "objective": objective,
                "likelihood_ratio": likelihood_ratio, "raw_likelihood_ratio": raw_lr,
                "nuisance_optimum": [float(v) for v in theta],
                "optimizer_message": message}

    def _profile_one(self, index: int) -> dict[str, Any]:
        name, estimate = self.names[index], float(self.fitted[index])
        lo, hi = self.bounds[index]
        cache: dict[float, dict[str, Any]] = {}

        def evaluate(value: float) -> dict[str, Any]:
            key = float(value)
            if key not in cache:
                cache[key] = self._evaluate(index, key)
            return cache[key]

        fitted_point = evaluate(estimate)
        if fitted_point["likelihood_ratio"] > 1e-4:
            raise ValueError(f"{name} profile does not nest the frozen optimum")
        if index in self.fixed or hi - lo <= _BOUND_TOL:
            reason = self.fixed.get(index, "collapsed working bound")
            return {
                "parameter": name, "estimate": estimate, "working_bounds": [lo, hi],
                "status": "fixed_unidentifiable", "fixed_reason": reason,
                "likelihood_support_interval": {
                    "lower": estimate, "upper": estimate,
                    "lower_clipped_to_bound": True, "upper_clipped_to_bound": True,
                },
                "at_lower_bound": abs(estimate - lo) <= _BOUND_TOL,
                "at_upper_bound": abs(estimate - hi) <= _BOUND_TOL,
                "evaluations": [fitted_point],
            }

        def endpoint(direction: int) -> tuple[float, bool]:
            bound = lo if direction < 0 else hi
            if abs(estimate - bound) <= _BOUND_TOL:
                evaluate(bound)
                return bound, True
            span = hi - lo
            step = span / 64.0
            inside = estimate
            while True:
                candidate = max(bound, estimate - step) if direction < 0 else min(bound, estimate + step)
                point = evaluate(candidate)
                if point["likelihood_ratio"] >= _LR_CUTOFF:
                    outside = candidate
                    for _ in range(40):
                        if abs(outside - inside) <= max(1e-7, span * 1e-7):
                            break
                        middle = (inside + outside) / 2.0
                        middle_point = evaluate(middle)
                        if middle_point["likelihood_ratio"] <= _LR_CUTOFF:
                            inside = middle
                        else:
                            outside = middle
                    return (inside + outside) / 2.0, False
                inside = candidate
                if candidate == bound:
                    return bound, True
                step = min(span, step * 2.0)

        lower, lower_clipped = endpoint(-1)
        upper, upper_clipped = endpoint(1)
        if lo == 0.0:
            evaluate(0.0)
        evaluations = [cache[key] for key in sorted(cache)]
        return {
            "parameter": name, "estimate": estimate, "working_bounds": [lo, hi],
            "status": "profiled",
            "likelihood_support_interval": {
                "lower": lower, "upper": upper,
                "lower_clipped_to_bound": lower_clipped,
                "upper_clipped_to_bound": upper_clipped,
            },
            "at_lower_bound": abs(estimate - lo) <= _BOUND_TOL,
            "at_upper_bound": abs(estimate - hi) <= _BOUND_TOL,
            "evaluations": evaluations,
        }

    def profiles(self) -> dict[str, Any]:
        return {name: self._profile_one(i) for i, name in enumerate(self.names)}


def _base_model_profile(name: str, model: Any, rows: Sequence[Mapping[str, Any]],
                        bundle: DirectionalBundle) -> dict[str, Any]:
    terms = tuple(model.terms)
    transform = bundle._base_transform() if terms else {}
    prepared = _prepare_directional(rows, terms, transform, bundle.local_level if terms else False)
    fitted = [model.intercept, *(model.coefficients[term] for term in terms), math.log(model.sigma)]
    names = ["intercept", *terms, "log_sigma"]
    fixed_terms = set(model.metadata.get("fixed_terms", []))
    fixed = {i + 1: "constant or unidentifiable standardized predictor"
             for i, term in enumerate(terms) if term in fixed_terms}
    bounds = [_BOUNDS[0]] + [(0.0, 0.0) if term in fixed_terms else _BOUNDS[1]
                              for term in terms] + [_BOUNDS[3]]
    vectorized = prepared.objective(np.asarray(fitted, dtype=float))
    scalar = _conditional_scalar(rows, np.asarray(fitted, dtype=float), terms, bundle)
    if abs(vectorized - scalar) > 1e-8 * (1.0 + abs(vectorized)):
        raise ValueError(f"{name} vectorized and scalar objectives disagree")
    profiler = _Profiler(prepared.objective, fitted, bounds, names, fixed)
    return {
        "fit_kind": model.metadata.get("fit_kind"), "row_count": len(rows),
        "frozen_objective": profiler.frozen_objective,
        "objective_scalar_difference": float(vectorized - scalar),
        "diagnostics": profiler.diagnostics(),
        "interval_scope": "working-model likelihood support; serial and measurement uncertainty are not calibrated",
        "profiles": profiler.profiles(),
    }


def _r0_profile(bundle: DirectionalBundle, rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    model = bundle.r0
    prepared = _prepare_remaining(rows)
    fitted = [model.intercept, math.log(model.sigma)]
    vectorized = prepared.objective(np.asarray(fitted, dtype=float))
    scalar = _r0_objective(np.asarray(fitted, dtype=float), rows)
    if abs(vectorized - scalar) > 1e-8 * (1.0 + abs(vectorized)):
        raise ValueError("R0 vectorized and scalar objectives disagree")
    profiler = _Profiler(prepared.objective, fitted, (_BOUNDS[0], _BOUNDS[3]),
                         ("intercept", "log_sigma"))
    return {
        "fit_kind": model.metadata.get("fit_kind"), "row_count": len(rows),
        "frozen_objective": profiler.frozen_objective,
        "objective_scalar_difference": float(vectorized - scalar),
        "diagnostics": profiler.diagnostics(),
        "interval_scope": "working-model likelihood support; serial and measurement uncertainty are not calibrated",
        "profiles": profiler.profiles(),
    }


def _mark_rows(q_rows: Sequence[Mapping[str, Any]], kind: str,
               joint_marks: bool) -> list[Mapping[str, Any]]:
    def valid(row: Mapping[str, Any], mark_kind: str) -> bool:
        return all(_mark_duration(row["feature"], float(endpoint), mark_kind) is not None
                   for endpoint in row["endpoints"])

    return [row for row in q_rows if valid(row, kind)
            and (not joint_marks or valid(row, "current" if kind == "previous" else "previous"))]


def _mark_profile(name: str, bundle: DirectionalBundle,
                  q_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    model = bundle.models[name]
    kind = "current" if name == "M3" else "previous"
    rows = _mark_rows(q_rows, kind, bundle.joint_marks)
    expected = int(model.metadata.get("n_fit", -1))
    if len(rows) != expected:
        raise ValueError(f"{name} profile mark population does not match frozen fit")
    beta_names = ("beta",) if bundle.mark_mode == "log_duration" else ("beta_type", "beta_within")
    fitted = [model.coefficients[term] for term in beta_names]
    fixed_indices = set(int(value) for value in model.metadata.get("fixed_beta_indices", []))
    fixed = {index: "constant or absent mark component" for index in fixed_indices}
    bounds = [(0.0, 0.0) if i in fixed_indices else
              ((0.0, 5.0) if bundle.directional else (-5.0, 5.0))
              for i in range(len(beta_names))]
    base = bundle.models["M2"]
    base_transform = bundle._base_transform()
    mark_transform = bundle._mark_transform(model)
    if not rows:
        if len(fixed_indices) != len(beta_names):
            raise ValueError(f"{name} has no profile rows but a free mark coefficient")
        objective = lambda beta: 0.0
        scalar = vectorized = 0.0
    else:
        prepared = _prepare_offset(rows, base, base_transform, mark_transform, kind,
                                   bundle.mark_mode, bundle.local_level)
        objective = prepared.objective
        vectorized = objective(np.asarray(fitted, dtype=float))
        scalar = _offset_objective(np.asarray(fitted, dtype=float), rows, base,
                                   base_transform, mark_transform, kind,
                                   bundle.mark_mode, bundle.local_level)
        if abs(vectorized - scalar) > 1e-8 * (1.0 + abs(vectorized)):
            raise ValueError(f"{name} vectorized and scalar objectives disagree")
    profiler = _Profiler(objective, fitted, bounds, beta_names, fixed)
    return {
        "fit_kind": model.metadata.get("fit_kind"), "row_count": len(rows),
        "baseline_model": "M2", "frozen_m2_nuisance": True,
        "frozen_objective": profiler.frozen_objective,
        "objective_scalar_difference": float(vectorized - scalar),
        "diagnostics": profiler.diagnostics(),
        "interval_scope": (
            "CONDITIONAL fixed-M2 likelihood-support interval; not a full "
            "nuisance-adjusted confidence interval; serial and measurement uncertainty are not calibrated"
        ),
        "profiles": profiler.profiles(),
    }


def profile_bundle(bundle: DirectionalBundle | Mapping[str, Any],
                   ledger: Sequence[Mapping[str, Any]],
                   evidence: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Profile a frozen directional fit without mutating it or its inputs."""
    frozen = _bundle(bundle)
    serialized_before = copy.deepcopy(frozen.to_dict())
    remaining, known, q_rows = _rows(frozen, ledger, evidence)
    result = {
        "schema_version": "a10d-fit-profile-v1",
        "likelihood_ratio_cutoff": _LR_CUTOFF,
        "support_delta_negative_log_likelihood": _DELTA_NLL,
        "models": {
            "R0": _r0_profile(frozen, remaining),
            "M0": _base_model_profile("M0", frozen.models["M0"], known, frozen),
            "M2": _base_model_profile("M2", frozen.models["M2"], q_rows, frozen),
            "M3": _mark_profile("M3", frozen, q_rows),
            "P3": _mark_profile("P3", frozen, q_rows),
        },
        "interpretation": {
            "support": "chi-square(1) 95% likelihood-ratio support using cutoff 3.841",
            "calibration_limit": "serial dependence and measurement uncertainty are not calibrated",
            "mark_limit": "M3/P3 profiles hold fitted M2 nuisance parameters fixed exactly",
        },
    }
    if frozen.to_dict() != serialized_before:
        raise RuntimeError("profile calculation mutated the frozen bundle")
    return result


__all__ = ["profile_bundle"]
