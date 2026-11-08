"""Evaluation-only association diagnostics for the A10f protocol.

The frozen forecast comparison does not call this module.  It fits signed
offsets to evaluation outcomes after scoring, with the timing baseline fitted
once on all timing-eligible rows and then held fixed.
"""

from __future__ import annotations

import copy
import math
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.optimize import minimize

from .directional_forecast import (
    DirectionalBundle,
    _PreparedOffset,
    _mark_components,
    _mark_duration,
    _mark_transform,
    _m2_covariates,
    _prepare_offset,
    fit_directional,
)
from .fit_profiles import _DELTA_NLL, _LR_CUTOFF, _Profiler, _rows, profile_bundle
from .ledger_forecast import ForecastModel, _conditional_node_loglik


_JOINT_NAMES = ("current_duration", "previous_duration")
_JOINT_STARTS = ((0.0, 0.0), (0.1, 0.1), (-0.1, -0.1))
_JOINT_BOUNDS = (-5.0, 5.0)


def _joint_rows(
    bundle: DirectionalBundle,
    ledger: Sequence[Mapping[str, Any]],
    evidence: Sequence[Mapping[str, Any]],
) -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]]]:
    q_rows = _rows(bundle, ledger, evidence)[2]
    common = []
    for row in q_rows:
        endpoints = row["endpoints"]
        current = [_mark_duration(row["feature"], float(endpoint), "current")
                   for endpoint in endpoints]
        previous = [_mark_duration(row["feature"], float(endpoint), "previous")
                    for endpoint in endpoints]
        if current and previous and all(value is not None for value in current + previous):
            common.append(row)
    return q_rows, common


def _prepare_joint_offset(
    rows: Sequence[Mapping[str, Any]],
    base: ForecastModel,
    base_transform: Mapping[str, Any],
    *,
    local_level: bool = True,
) -> tuple[_PreparedOffset, dict[str, dict[str, Any]], tuple[int, ...]]:
    if not rows:
        raise ValueError("joint association has no common current/previous-mark rows")
    current_transform, current_indices = _mark_transform(
        rows, "current", "log_duration", "point"
    )
    previous_transform, previous_indices = _mark_transform(
        rows, "previous", "log_duration", "point"
    )
    expected = list(range(len(rows)))
    if current_indices != expected or previous_indices != expected:
        raise ValueError("joint association rows do not all have both marks")
    current = _prepare_offset(
        rows, base, base_transform, current_transform, "current", "log_duration", local_level
    )
    previous = _prepare_offset(
        rows, base, base_transform, previous_transform, "previous", "log_duration", local_level
    )
    shared_arrays = (
        "base_mu", "interval_lower", "interval_upper", "censor_time", "age",
        "is_interval", "node_log_weights",
    )
    if any(not np.array_equal(getattr(current, name), getattr(previous, name))
           for name in shared_arrays) or current.sigma != previous.sigma:
        raise RuntimeError("joint mark preparations do not share the same baseline likelihood")
    marks = np.concatenate((current.marks, previous.marks), axis=2)
    prepared = _PreparedOffset(
        current.base_mu,
        marks,
        current.interval_lower,
        current.interval_upper,
        current.censor_time,
        current.age,
        current.is_interval,
        current.node_log_weights,
        current.sigma,
    )
    transforms = {"current": current_transform, "previous": previous_transform}
    fixed = tuple(index for index, name in enumerate(("current", "previous"))
                  if transforms[name].get("mark_fixed"))
    return prepared, transforms, fixed


def _joint_offset_objective(
    beta: np.ndarray,
    rows: Sequence[Mapping[str, Any]],
    base: ForecastModel,
    base_transform: Mapping[str, Any],
    transforms: Mapping[str, Mapping[str, Any]],
    *,
    local_level: bool = True,
) -> float:
    coefficients = np.asarray(beta, dtype=float)
    if coefficients.shape != (2,):
        raise ValueError("joint association requires two mark coefficients")
    log_likelihood = 0.0
    for row in rows:
        feature, outcome, endpoints = row["feature"], row["evidence"], row["endpoints"]
        covariates = _m2_covariates(feature, base_transform, local_level)
        base_mu = base.intercept + sum(
            base.coefficients[name] * covariates[name] for name in base.terms
        )
        numerators, denominators = [], []
        for endpoint in endpoints:
            point = float(endpoint)
            current = _mark_duration(feature, point, "current")
            previous = _mark_duration(feature, point, "previous")
            if current is None or previous is None:
                raise ValueError("joint scalar objective requires both marks")
            marks = np.array([
                _mark_components(current, "log_duration", transforms["current"])[0],
                _mark_components(previous, "log_duration", transforms["previous"])[0],
            ])
            mu = base_mu + float(np.dot(coefficients, marks))
            numerator, denominator = _conditional_node_loglik(
                outcome, point, mu, base.sigma
            )
            numerators.append(numerator)
            denominators.append(denominator)
        log_likelihood += float(
            np.logaddexp.reduce(numerators) - np.logaddexp.reduce(denominators)
        )
    value = -log_likelihood
    return value if math.isfinite(value) else 1e100


def _identifiability(
    prepared: _PreparedOffset,
    fixed: Sequence[int],
) -> dict[str, Any]:
    active = np.isfinite(prepared.node_log_weights)
    design = prepared.marks[active]
    free = [index for index in range(2) if index not in fixed]
    free_design = design[:, free] if free else np.empty((len(design), 0))
    if free:
        singular = np.linalg.svd(free_design, compute_uv=False)
        tolerance = (max(max(free_design.shape) * np.finfo(float).eps, 1e-10)
                     * singular[0] if len(singular) and singular[0] > 0.0 else 0.0)
        rank = int(np.sum(singular > tolerance))
        condition = (float(singular[0] / singular[-1])
                     if rank == len(free) and singular[-1] > 0.0 else None)
    else:
        singular, tolerance, rank, condition = np.array([]), 0.0, 0, None
    full_rank = rank == len(free)
    parameters = {}
    for index, name in enumerate(_JOINT_NAMES):
        if index in fixed:
            status = "fixed_constant"
        elif full_rank:
            status = "design_identified"
        else:
            status = "not_coefficient_identified_joint_collinearity"
        parameters[name] = status
    return {
        "active_design_rows": int(design.shape[0]),
        "free_parameter_count": len(free),
        "design_rank": rank,
        "full_column_rank": full_rank,
        "singular_values": [float(value) for value in singular],
        "rank_tolerance": float(tolerance),
        "condition_number": condition,
        "coefficient_status": parameters,
        "all_free_coefficients_design_identified": bool(full_rank),
    }


def _fit_joint(
    prepared: _PreparedOffset,
    fixed: Sequence[int],
) -> tuple[np.ndarray, list[dict[str, Any]], list[dict[str, Any]], str]:
    fixed_set = set(fixed)
    free = [index for index in range(2) if index not in fixed_set]
    if not free:
        beta = np.zeros(2, dtype=float)
        objective = float(prepared.objective(beta))
        if not math.isfinite(objective) or objective >= 1e99:
            raise ValueError("fixed joint association likelihood is invalid")
        return beta, [{
            "start": [0.0, 0.0], "solution": [0.0, 0.0],
            "objective": objective, "message": "both mark predictors are constant",
        }], [], "fixed_constant"

    successful: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    candidates: list[tuple[float, int, np.ndarray]] = []
    for order, raw_start in enumerate(_JOINT_STARTS):
        start = np.asarray(raw_start, dtype=float)
        start[list(fixed_set)] = 0.0

        def reduced(values: np.ndarray) -> float:
            beta = np.zeros(2, dtype=float)
            beta[free] = values
            return prepared.objective(beta)

        result = minimize(
            reduced,
            start[free],
            method="L-BFGS-B",
            bounds=[_JOINT_BOUNDS for _ in free],
        )
        solution = np.zeros(2, dtype=float)
        if len(result.x) == len(free):
            solution[free] = result.x
        gradient = np.asarray(result.jac, dtype=float) if result.jac is not None else np.array([])
        valid = (
            bool(result.success)
            and len(result.x) == len(free)
            and np.all(np.isfinite(result.x))
            and math.isfinite(float(result.fun))
            and float(result.fun) < 1e99
            and len(gradient) == len(free)
            and np.all(np.isfinite(gradient))
        )
        record = {
            "start": [float(value) for value in start],
            "solution": [float(value) for value in solution],
            "objective": (float(result.fun) if math.isfinite(float(result.fun)) else None),
            "message": str(result.message),
        }
        if valid:
            successful.append(record)
            candidates.append((float(result.fun), order, solution))
        else:
            failed.append({**record, "success": bool(result.success)})
    if not candidates:
        raise ValueError(f"joint association optimization failed: {failed}")
    _, _, beta = min(candidates, key=lambda value: (value[0], value[1]))
    return beta, successful, failed, "optimized"


def _joint_association(
    bundle: DirectionalBundle,
    ledger: Sequence[Mapping[str, Any]],
    evidence: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    q_rows, common_rows = _joint_rows(bundle, ledger, evidence)
    if not common_rows:
        return {
            "status": "not_estimable",
            "reason": "no timing-eligible rows have both current and previous duration marks",
            "timing_eligible_count": len(q_rows),
            "joint_valid_count": 0,
            "baseline_model": "the staged evaluation M2 fit on all timing-eligible rows",
            "frozen_m2_nuisance": True,
        }
    base = bundle.models["M2"]
    base_transform = bundle._base_transform()
    prepared, transforms, fixed = _prepare_joint_offset(
        common_rows, base, base_transform, local_level=bundle.local_level
    )
    beta, successful, failed, fit_status = _fit_joint(prepared, fixed)
    vectorized = float(prepared.objective(beta))
    scalar = _joint_offset_objective(
        beta, common_rows, base, base_transform, transforms,
        local_level=bundle.local_level,
    )
    tolerance = 1e-8 * (1.0 + abs(vectorized))
    if abs(vectorized - scalar) > tolerance:
        raise ValueError("joint vectorized and scalar objectives disagree")
    bounds = [(0.0, 0.0) if index in fixed else _JOINT_BOUNDS for index in range(2)]
    fixed_reasons = {index: "constant standardized mark on joint-valid rows" for index in fixed}
    identifiability = _identifiability(prepared, fixed)
    profiler = _Profiler(prepared.objective, beta, bounds, _JOINT_NAMES, fixed_reasons)
    if identifiability["full_column_rank"]:
        profiles = profiler.profiles()
        for index, name in enumerate(_JOINT_NAMES):
            profiles[name]["coefficient_identified"] = index not in fixed
            if index in fixed:
                profiles[name]["identifiability_status"] = (
                    "mark is constant on joint-valid rows and its coefficient is fixed at zero"
                )
    else:
        profiles = {
            name: {
                "parameter": name,
                "estimate": float(beta[index]),
                "working_bounds": [float(bounds[index][0]), float(bounds[index][1])],
                "status": "not_coefficient_identified_joint_collinearity",
                "coefficient_identified": False,
                "identifiability_status": (
                    "joint design is rank deficient; coefficient-specific likelihood support "
                    "is not reported"
                ),
                "likelihood_support_interval": None,
            }
            for index, name in enumerate(_JOINT_NAMES)
        }
    return {
        "status": "fitted",
        "fit_status": fit_status,
        "timing_eligible_count": len(q_rows),
        "joint_valid_count": len(common_rows),
        "baseline_model": "the staged evaluation M2 fit on all timing-eligible rows",
        "frozen_m2_nuisance": True,
        "coefficients": {
            "current_duration": float(beta[0]),
            "previous_duration": float(beta[1]),
        },
        "bounds": [[float(lo), float(hi)] for lo, hi in bounds],
        "transforms": {
            name: {
                "log_duration_center": float(transforms[name]["mark_center"]),
                "log_duration_scale": float(transforms[name]["mark_scale"]),
                "fixed_constant": bool(transforms[name].get("mark_fixed")),
            }
            for name in ("current", "previous")
        },
        "objective": vectorized,
        "scalar_objective_difference": vectorized - scalar,
        "successful_starts": successful,
        "failed_starts": failed,
        "identifiability": identifiability,
        "profile_diagnostics": profiler.diagnostics(),
        "likelihood_ratio_cutoff": _LR_CUTOFF,
        "support_delta_negative_log_likelihood": _DELTA_NLL,
        "profiles": profiles,
        "interval_scope": (
            "CONDITIONAL fixed-M2 likelihood support; the other mark offset is reoptimized. "
            "This is not a serial-dependence- or measurement-calibrated confidence interval."
        ),
    }


def evaluation_association(
    ledger: Sequence[Mapping[str, Any]],
    evidence: Sequence[Mapping[str, Any]],
    cutoff: float,
) -> dict[str, Any]:
    """Fit serializable evaluation-only association diagnostics.

    The signed one-mark fits and M2 timing baseline are fitted once.  The joint
    fit reuses that exact M2 baseline and refits no forecast parameter.
    """
    ledger_before = copy.deepcopy(ledger)
    evidence_before = copy.deepcopy(evidence)
    staged = fit_directional(ledger, evidence, cutoff, directional=False)
    staged_profile = profile_bundle(staged, ledger, evidence)
    result = {
        "schema_version": "a10f-evaluation-association-v1",
        "scope": (
            "evaluation-only conditional association diagnostic; no model or coefficient "
            "enters the frozen confirmatory forecasts"
        ),
        "cutoff": float(cutoff),
        "staged": {
            "bundle": staged.to_dict(),
            "profiles": {
                name: staged_profile["models"][name] for name in ("M2", "M3", "P3")
            },
            "profile_metadata": {
                "schema_version": staged_profile["schema_version"],
                "likelihood_ratio_cutoff": staged_profile["likelihood_ratio_cutoff"],
                "support_delta_negative_log_likelihood": staged_profile[
                    "support_delta_negative_log_likelihood"
                ],
                "interpretation": staged_profile["interpretation"],
            },
        },
        "joint": _joint_association(staged, ledger, evidence),
        "interpretation": {
            "forecast_claim": "none",
            "mechanism_claim": "none",
            "limits": (
                "Association estimates are conditional on the fixed evaluation M2 baseline, "
                "the extracted score-eligible rows, and the working landmark likelihood."
            ),
        },
    }
    if ledger != ledger_before or evidence != evidence_before:
        raise RuntimeError("evaluation association mutated its ledger or evidence input")
    return result


__all__ = ["evaluation_association"]
