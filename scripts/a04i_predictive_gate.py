#!/usr/bin/env python3
"""Fail-closed blockwise predictive gate for A04i benchmark qualification.

For ``n`` independent synthetic real-sized vectors, unbiased covariance ``S``,
and one independent real vector, define ``Q = (x - mean)' S^-1 (x - mean)``.
Under a multivariate-normal reference process,

    n (n - p) Q / (p (n - 1) (n + 1)) ~ F(p, n - p).

This is a one-new-vector prediction result, not inference on the synthetic
mean. Each block uses its own nominal alpha and an additional unadjusted
marginal cap; no overall nominal error rate is claimed.

The direct upper-F tail follows the beta identity documented by R ``stats``:
https://stat.ethz.ch/R-manual/R-devel/library/stats/html/Fdist.html
Reference values were checked with ``Rscript`` ``qf`` and ``pf``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
import statistics as st
import sys
from typing import Any

from a04h_morphology_targets import betainc


MIN_REPLICATES = 150
BLOCK_ALPHA = 0.01
Z_MAX = 3.3
MAX_CONDITION = 1.0e12
_PIVOT_TOLERANCE = 64.0 * sys.float_info.epsilon


class GateValidationError(ValueError):
    """A controlled fail-closed validation error for a predictive block."""


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise GateValidationError(f"{label} must be finite numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise GateValidationError(f"{label} must be finite numeric") from exc
    if not math.isfinite(result):
        raise GateValidationError(f"{label} must be finite numeric")
    return result


def f_sf(value: float, d1: int, d2: int) -> float:
    """Return the central-F upper tail directly, without subtracting its CDF."""
    value = _finite(value, "F statistic")
    if value < 0:
        raise GateValidationError("F statistic must be nonnegative")
    if isinstance(d1, bool) or isinstance(d2, bool) or not isinstance(d1, int) or not isinstance(d2, int):
        raise GateValidationError("F degrees of freedom must be positive integers")
    if d1 <= 0 or d2 <= 0:
        raise GateValidationError("F degrees of freedom must be positive integers")
    x = d2 / (d2 + d1 * value)
    result = betainc(d2 / 2.0, d1 / 2.0, x)
    if not math.isfinite(result) or not 0.0 <= result <= 1.0:
        raise GateValidationError("F upper-tail evaluation was invalid")
    return result


def hotelling_prediction_f(q: float, n: int, p: int) -> float:
    """Scale a one-new-vector Hotelling quadratic form to its F reference."""
    q = _finite(q, "Hotelling quadratic form")
    if q < 0.0:
        raise GateValidationError("Hotelling quadratic form must be nonnegative")
    if any(isinstance(value, bool) or not isinstance(value, int) for value in (n, p)):
        raise GateValidationError("replicate count and dimension must be positive integers")
    if p <= 0 or n <= p:
        raise GateValidationError("replicate count must exceed the positive block dimension")
    result = q * n * (n - p) / (p * (n - 1) * (n + 1))
    if not math.isfinite(result):
        raise GateValidationError("scaled Hotelling statistic was nonfinite")
    return result


def _cholesky(matrix: list[list[float]]) -> list[list[float]]:
    size = len(matrix)
    factor = [[0.0] * size for _ in range(size)]
    tolerance = _PIVOT_TOLERANCE * max(1, size)
    for row in range(size):
        for column in range(row + 1):
            value = matrix[row][column] - sum(
                factor[row][k] * factor[column][k] for k in range(column)
            )
            if column == row:
                if not math.isfinite(value) or value <= tolerance:
                    raise GateValidationError("covariance is singular or not positive definite")
                factor[row][column] = math.sqrt(value)
            else:
                factor[row][column] = value / factor[column][column]
    return factor


def _cholesky_solve(factor: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    forward = [0.0] * size
    for row in range(size):
        forward[row] = (
            vector[row] - sum(factor[row][column] * forward[column] for column in range(row))
        ) / factor[row][row]
    result = [0.0] * size
    for row in range(size - 1, -1, -1):
        result[row] = (
            forward[row]
            - sum(factor[column][row] * result[column] for column in range(row + 1, size))
        ) / factor[row][row]
    if any(not math.isfinite(value) for value in result):
        raise GateValidationError("covariance solve produced a nonfinite result")
    return result


def _condition_inf(matrix: list[list[float]], factor: list[list[float]]) -> float:
    size = len(matrix)
    norm = max(sum(abs(value) for value in row) for row in matrix)
    inverse = [[0.0] * size for _ in range(size)]
    for column in range(size):
        unit = [0.0] * size
        unit[column] = 1.0
        solution = _cholesky_solve(factor, unit)
        for row, value in enumerate(solution):
            inverse[row][column] = value
    inverse_norm = max(sum(abs(value) for value in row) for row in inverse)
    result = norm * inverse_norm
    if not math.isfinite(result):
        raise GateValidationError("covariance condition estimate was nonfinite")
    return result


def _invalid_result(
    reason: str,
    names: Sequence[str],
    replicates: int | None,
    alpha: float,
    z_max: float,
) -> dict[str, Any]:
    return {
        "valid": False,
        "qualified": False,
        "pass": False,
        "reason": reason,
        "statistics": list(names),
        "replicates": replicates,
        "block_alpha": alpha,
        "z_max": z_max,
        "scope": "blockwise normal-reference prediction; no overall nominal rate",
    }


def _check_block(
    real: Mapping[str, Any],
    replicates: Sequence[Mapping[str, Any]],
    names: Sequence[str],
    *,
    alpha: float,
    z_max: float,
    min_replicates: int,
    max_condition: float,
) -> dict[str, Any]:
    if isinstance(names, (str, bytes)) or not isinstance(names, Sequence):
        raise GateValidationError("statistics must be a nonempty sequence of names")
    names = tuple(names)
    if not names or any(not isinstance(name, str) or not name for name in names):
        raise GateValidationError("statistics must be a nonempty sequence of names")
    if len(set(names)) != len(names):
        raise GateValidationError("statistic names must be unique")
    if not isinstance(real, Mapping):
        raise GateValidationError("real vector must be a mapping")
    if isinstance(replicates, (str, bytes)) or not isinstance(replicates, Sequence):
        raise GateValidationError("replicates must be a sequence of mappings")
    if isinstance(min_replicates, bool) or not isinstance(min_replicates, int) or min_replicates < MIN_REPLICATES:
        raise GateValidationError(f"minimum replicate requirement must be at least {MIN_REPLICATES}")
    n, p = len(replicates), len(names)
    if n < min_replicates:
        raise GateValidationError(f"need at least {min_replicates} replicate vectors; received {n}")
    if n <= p:
        raise GateValidationError("replicate count must exceed block dimension")
    alpha = _finite(alpha, "block alpha")
    z_max = _finite(z_max, "marginal z cap")
    max_condition = _finite(max_condition, "maximum covariance condition")
    if not 0.0 < alpha < 1.0:
        raise GateValidationError("block alpha must lie strictly between zero and one")
    if z_max <= 0:
        raise GateValidationError("marginal z cap must be positive")
    if max_condition <= 1.0:
        raise GateValidationError("maximum covariance condition must exceed one")

    try:
        real_values = [_finite(real[name], f"real[{name!r}]") for name in names]
    except KeyError as exc:
        raise GateValidationError(f"real vector is missing statistic {exc.args[0]!r}") from exc
    columns = [[] for _ in names]
    for index, replicate in enumerate(replicates):
        if not isinstance(replicate, Mapping):
            raise GateValidationError(f"replicates[{index}] must be a mapping")
        for column, name in zip(columns, names):
            try:
                column.append(_finite(replicate[name], f"replicates[{index}][{name!r}]"))
            except KeyError as exc:
                raise GateValidationError(
                    f"replicates[{index}] is missing statistic {exc.args[0]!r}"
                ) from exc

    means = [st.fmean(column) for column in columns]
    covariance = [[0.0] * p for _ in range(p)]
    for row in range(p):
        for column in range(row + 1):
            value = sum(
                (columns[row][index] - means[row]) * (columns[column][index] - means[column])
                for index in range(n)
            ) / (n - 1)
            if not math.isfinite(value):
                raise GateValidationError("covariance contains a nonfinite value")
            covariance[row][column] = covariance[column][row] = value
    variances = [covariance[index][index] for index in range(p)]
    if any(not math.isfinite(value) or value <= 0.0 for value in variances):
        raise GateValidationError("every statistic must have positive finite replicate variance")
    standard_deviations = [math.sqrt(value) for value in variances]
    correlation = [
        [covariance[row][column] / (standard_deviations[row] * standard_deviations[column]) for column in range(p)]
        for row in range(p)
    ]
    if any(not math.isfinite(value) for row in correlation for value in row):
        raise GateValidationError("standardized covariance contains a nonfinite value")
    factor = _cholesky(correlation)
    condition = _condition_inf(correlation, factor)
    if condition > max_condition:
        raise GateValidationError(
            f"standardized covariance is ill-conditioned ({condition:.6g} > {max_condition:.6g})"
        )

    z_values = [
        (real_values[index] - means[index]) / standard_deviations[index] for index in range(p)
    ]
    solution = _cholesky_solve(factor, z_values)
    q = sum(value * solved for value, solved in zip(z_values, solution))
    if not math.isfinite(q) or q < 0.0:
        raise GateValidationError("Hotelling quadratic form was invalid")
    f_value = hotelling_prediction_f(q, n, p)
    prediction_p = f_sf(f_value, p, n - p)
    joint_pass = prediction_p >= alpha
    marginal_pass = all(abs(value) <= z_max for value in z_values)
    qualified = joint_pass and marginal_pass

    return {
        "valid": True,
        "qualified": qualified,
        "pass": qualified,
        "reason": None,
        "statistics": list(names),
        "replicates": n,
        "dimension": p,
        "block_alpha": alpha,
        "z_max": z_max,
        "synthetic_mean": dict(zip(names, means)),
        "synthetic_sd": dict(zip(names, standard_deviations)),
        "z_raw": dict(zip(names, z_values)),
        "hotelling_q": q,
        "f_statistic": f_value,
        "f_df1": p,
        "f_df2": n - p,
        "prediction_p_raw": prediction_p,
        "covariance_condition_inf": condition,
        "joint_pass": joint_pass,
        "marginal_pass": marginal_pass,
        "display": {
            "synthetic_mean": {name: round(value, 4) for name, value in zip(names, means)},
            "synthetic_sd": {
                name: round(value, 4) for name, value in zip(names, standard_deviations)
            },
            "z": {name: round(value, 2) for name, value in zip(names, z_values)},
            "hotelling_q": round(q, 6),
            "f_statistic": round(f_value, 6),
            "prediction_p": round(prediction_p, 8),
            "covariance_condition_inf": round(condition, 6),
        },
        "scope": "blockwise normal-reference prediction; no overall nominal rate",
    }


def check_block(
    real: Mapping[str, Any],
    replicates: Sequence[Mapping[str, Any]],
    names: Sequence[str],
    *,
    alpha: float = BLOCK_ALPHA,
    z_max: float = Z_MAX,
    min_replicates: int = MIN_REPLICATES,
    max_condition: float = MAX_CONDITION,
) -> dict[str, Any]:
    """Evaluate one block, returning an explicit unqualified result on invalid input."""
    replicate_count = len(replicates) if isinstance(replicates, Sequence) else None
    result_names = tuple(names) if isinstance(names, Sequence) and not isinstance(names, (str, bytes)) else ()
    try:
        return _check_block(
            real,
            replicates,
            names,
            alpha=alpha,
            z_max=z_max,
            min_replicates=min_replicates,
            max_condition=max_condition,
        )
    except GateValidationError as exc:
        return _invalid_result(str(exc), result_names, replicate_count, alpha, z_max)

