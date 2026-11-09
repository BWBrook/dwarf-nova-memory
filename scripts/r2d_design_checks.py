"""Invented-number R2d design checks; no observations, real fits or simulations."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    "docs/protocols/r2d-sealed-design-v0.md",
    "docs/audits/2026-11-09-claude-r2b-review.md",
    "scripts/r2b_claude_review_checks.py",
    "docs/protocols/r2d-sealed-design-v1.md",
    "src/dnmem/r2d_simulation.py",
    "scripts/r2d_precision.py",
    "data/provenance/r2d_precision/design.json",
    "scripts/r2d_design_checks.py",
]


def centered_covariance(window, lag):
    coefficients = [1.] + [-1. / window] * window
    return sum(coefficients[j] * coefficients[j + lag]
               for j in range(len(coefficients) - lag))


def checks():
    beta, fitted, n = .05, .2, 5000
    candidate_gain = fitted * beta - fitted ** 2 / 2
    assert beta > 0 and candidate_gain < 0

    k_mark, k_level, a, b, time = 10, 20, .02, .01, 100
    mark = a * time - sum(a * (time - j) for j in range(1, k_mark + 1)) / k_mark
    residual = b * time - sum(b * (time - j) for j in range(1, k_level + 1)) / k_level
    score = mark * residual
    formula = (k_mark + 1) * (k_level + 1) * a * b / 4
    assert math.isclose(score, formula, abs_tol=1e-14)
    shift = .1 * mark
    trend_gain = shift * residual - shift ** 2 / 2
    assert trend_gain > 0

    lag_rows = []
    for lag in range(1, 11):
        cm = centered_covariance(k_mark, lag)
        ce = centered_covariance(k_level, lag)
        assert math.isclose(cm, -lag / k_mark ** 2, abs_tol=1e-14)
        assert math.isclose(ce, -lag / k_level ** 2, abs_tol=1e-14)
        lag_rows.append(dict(lag=lag, mark_covariance=cm,
                             recalibrated_error_covariance=ce, score_covariance=cm * ce))
    variance = (1 + 1 / k_mark) * (1 + 1 / k_level)
    long_run_variance = variance + 2 * sum(row["score_covariance"] for row in lag_rows)

    positive, negative = .126, -.126
    heterogeneous_gain = (positive ** 2 + negative ** 2) / 4
    pooled_signal = (positive + negative) / 2
    assert heterogeneous_gain > 0 and pooled_signal == 0

    return dict(
        scope="Invented Gaussian location and deterministic trend arithmetic only; no astronomy data, real fits or scored forecasts",
        positive_score_negative_frozen_gain=dict(
            true_coefficient=beta, development_fitted_coefficient=fitted,
            score_expectation=beta, conditional_expected_gain=candidate_gain,
            known_variance_score_noncentrality_at_n=beta * math.sqrt(n), n=n,
            meaning="A positive score direction need not improve the fixed development-trained candidate"),
        rolling_guards_leave_shared_trend=dict(
            mark_slope=a, outcome_level_slope=b, previous_marks=k_mark,
            previous_resolved_outcomes=k_level, centered_mark=mark,
            residual_mean=residual, score_expectation=score,
            analytic_score_expectation=formula, fitted_candidate_coefficient=.1,
            conditional_expected_gain=trend_gain, no_direct_mark_effect=True,
            meaning="Shared trend is predictive over the lagging base: specificity stress, not a strict predictive-null false positive"),
        guard_induced_dependence=dict(
            assumption="Independent iid centered mark and residual streams before the rolling operations; unit variances; instantaneous outcome availability",
            lags=lag_rows, instantaneous_score_variance=variance,
            long_run_score_variance=long_run_variance, variance_ratio=long_run_variance / variance,
            meaning="Rolling guards induce score dependence even without raw serial dependence"),
        exact_sign_flip_granularity=[dict(
            independent_symmetric_stars=s, one_sided_minimum_p=2. ** (-s),
            can_reject_at_five_percent=2. ** (-s) <= .05) for s in range(3, 9)],
        heterogeneous_signs=dict(
            star_coefficients=[positive, negative], mean_individual_oracle_kl=heterogeneous_gain,
            pooled_score_mean=pooled_signal, pooled_optimal_coefficient=0, pooled_optimal_gain=0,
            meaning="Mean individual oracle KL is not pooled one-sided information"),
        source_sha256={name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New JSON output file; existing evidence is never overwritten")
    args = parser.parse_args()
    result = checks()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"output": str(args.output), "checks": 5, "scope": result["scope"]}))


if __name__ == "__main__":
    main()
