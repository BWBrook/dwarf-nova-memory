"""Independent calculations for the pre-production A10c methods audit."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.special import log_ndtr
from scipy.stats import beta, binom


OUT = Path(__file__).resolve().parents[1] / "data/provenance/a10d_design_calculations.json"


def log_survival(age: np.ndarray, mu: np.ndarray, sigma: float) -> np.ndarray:
    return log_ndtr(-(np.log(age) - mu) / sigma)


def counterexample() -> dict:
    # A and epsilon are independent and equiprobable. Q=5 with probability 0.9
    # and Q=20 with probability 0.1. Retain observed anchors with ahat >= 0
    # that are alive at true issue age A. True duration is always 10.
    states = []
    for age in (2.0, 8.0):
        for epsilon in (0.0, 6.0):
            for q, q_probability in ((5.0, 0.9), (20.0, 0.1)):
                probability = 0.25 * q_probability
                ahat = age - epsilon
                if ahat < 0 or not age < q:
                    continue
                states.append(
                    {
                        "A": age,
                        "epsilon": epsilon,
                        "Q": q,
                        "ahat": ahat,
                        "Dhat": 10.0 + epsilon,
                        "Qhat": q - epsilon,
                        "R": q - age,
                        "raw_probability": probability,
                    }
                )
    total = sum(row["raw_probability"] for row in states)
    for row in states:
        row["weight"] = row["raw_probability"] / total

    at_two = [row for row in states if row["ahat"] == 2.0]
    at_two_total = sum(row["weight"] for row in at_two)
    for row in at_two:
        row["conditional_weight_at_ahat_2"] = row["weight"] / at_two_total

    # At ahat=2, Dhat and remaining wait have disjoint support. Therefore the
    # exact mutual information is H(Dhat | ahat=2, retained, alive).
    p_high = sum(
        row["conditional_weight_at_ahat_2"] for row in at_two if row["Dhat"] == 16.0
    )
    information = -p_high * math.log(p_high) - (1.0 - p_high) * math.log(1.0 - p_high)

    # Fit the same directional conditional-lognormal form to the retained
    # population, using a binary duration contrast. The weights are exact
    # population probabilities, so this is not a Monte Carlo result.
    ages = np.array([row["ahat"] for row in states])
    qhats = np.array([row["Qhat"] for row in states])
    x = np.array([float(row["Dhat"] == 16.0) for row in states])
    weights = np.array([row["weight"] for row in states])

    def objective(theta: np.ndarray, include_mark: bool) -> float:
        alpha = float(theta[0])
        mark = float(theta[1]) if include_mark else 0.0
        log_sigma = float(theta[-1])
        sigma = math.exp(log_sigma)
        mu = alpha + mark * x
        z = (np.log(qhats) - mu) / sigma
        log_density = -np.log(qhats) - log_sigma - 0.5 * math.log(2 * math.pi) - 0.5 * z**2
        ll = log_density - log_survival(ages, mu, sigma)
        return -float(np.dot(weights, ll))

    base_fits = [
        minimize(
            lambda theta: objective(theta, False),
            np.array([alpha, log_sigma]),
            method="L-BFGS-B",
            bounds=((-2.0, 8.0), (-4.0, 2.0)),
        )
        for alpha in (math.log(5.0), math.log(10.0), math.log(20.0))
        for log_sigma in (math.log(0.3), math.log(0.8), math.log(1.5))
    ]
    base = min(base_fits, key=lambda result: result.fun)
    marked_fits = [
        minimize(
            lambda theta: objective(theta, True),
            np.array([base.x[0], beta_start, log_sigma]),
            method="L-BFGS-B",
            bounds=((-2.0, 8.0), (0.0, 5.0), (-4.0, 2.0)),
        )
        for beta_start in (0.0, 0.5, 1.5, 3.0)
        for log_sigma in (math.log(0.3), base.x[-1], math.log(1.2))
    ]
    marked = min(marked_fits, key=lambda result: result.fun)
    return {
        "states": states,
        "p_high_duration_given_ahat_2": p_high,
        "mutual_information_nats_at_ahat_2": information,
        "mean_remaining_wait_at_ahat_2": {
            "Dhat_10": sum(
                row["R"] * row["conditional_weight_at_ahat_2"]
                for row in at_two
                if row["Dhat"] == 10.0
            )
            / (1.0 - p_high),
            "Dhat_16": sum(
                row["R"] * row["conditional_weight_at_ahat_2"]
                for row in at_two
                if row["Dhat"] == 16.0
            )
            / p_high,
        },
        "conditional_lognormal_fit": {
            "base_success": bool(base.success),
            "base_alpha": float(base.x[0]),
            "base_sigma": math.exp(float(base.x[-1])),
            "base_expected_log_score": -float(base.fun),
            "marked_success": bool(marked.success),
            "marked_alpha": float(marked.x[0]),
            "marked_beta_binary_Dhat16": float(marked.x[1]),
            "marked_sigma": math.exp(float(marked.x[-1])),
            "marked_expected_log_score": -float(marked.fun),
            "gain_nats_per_retained_anchor": float(base.fun - marked.fun),
        },
    }


def partial_correlations() -> list[dict]:
    rows = []
    marginal = 0.13
    for phi in (0.9, 0.98):
        current = (marginal - (marginal * phi) ** 2) / (1.0 - (marginal * phi) ** 2)
        previous = marginal * phi * (1.0 - marginal) / math.sqrt(
            (1.0 - (marginal * phi) ** 2) * (1.0 - marginal**2)
        )
        # Small root that makes the current-duration partial correlation 0.13.
        target = 0.13
        discriminant = 1.0 - 4.0 * (1.0 - target) * phi**2 * target
        calibrated_loading_sq = (1.0 - math.sqrt(discriminant)) / (
            2.0 * (1.0 - target) * phi**2
        )

        # Also condition on the protocol's idealized local level: the raw mean
        # of Q[n-2], ..., Q[n-7], assuming all six are observed. Standardizing
        # L does not change these partial correlations.
        var_l = (
            6.0
            + 2.0
            * sum((6 - lag) * marginal * phi**lag for lag in range(1, 6))
        ) / 36.0
        cov_qprev_l = marginal * sum(phi**lag for lag in range(1, 7)) / 6.0
        cov_current_l = marginal * sum(phi**lag for lag in range(2, 8)) / 6.0
        z_cov = np.array([[1.0, cov_qprev_l], [cov_qprev_l, var_l]])
        z_inv = np.linalg.inv(z_cov)
        c_current = np.array([marginal * phi, cov_current_l])
        explained_current = float(c_current @ z_inv @ c_current)
        current_with_l = (marginal - explained_current) / (1.0 - explained_current)

        c_previous_duration = np.array([marginal, cov_qprev_l])
        residual_cov_previous = marginal * phi - float(
            c_current @ z_inv @ c_previous_duration
        )
        residual_var_previous = 1.0 - float(
            c_previous_duration @ z_inv @ c_previous_duration
        )
        previous_with_l = residual_cov_previous / math.sqrt(
            (1.0 - explained_current) * residual_var_previous
        )
        rows.append(
            {
                "phi": phi,
                "lambda_squared": marginal,
                "marginal_corr_Dn_Qn": marginal,
                "partial_corr_Dn_Qn_given_Qprev": current,
                "partial_corr_Dprev_Qn_given_Qprev": previous,
                "partial_corr_Dn_Qn_given_Qprev_and_six_gap_level": current_with_l,
                "partial_corr_Dprev_Qn_given_Qprev_and_six_gap_level": previous_with_l,
                "gaussian_information_gain_current_nats_given_Qprev_and_level": -0.5
                * math.log1p(-(current_with_l**2)),
                "gaussian_information_gain_previous_nats_given_Qprev_and_level": -0.5
                * math.log1p(-(previous_with_l**2)),
                "lambda_squared_for_partial_0.13": calibrated_loading_sq,
            }
        )
    return rows


def offset_counterexample(states):
    ages = np.asarray([row["ahat"] for row in states])
    q = np.asarray([row["Qhat"] for row in states])
    weights = np.asarray([row["weight"] for row in states])
    log_d = np.log([row["Dhat"] for row in states])
    center = float(np.dot(weights, log_d))
    scale = math.sqrt(float(np.dot(weights, (log_d-center)**2)))
    x = (log_d-center)/scale

    def nll(alpha, sigma, mark):
        mu = alpha+mark*x
        lo, hi = (np.log(q-.01)-mu)/sigma, (np.log(q+.01)-mu)/sigma
        log_hi = np.where(lo > 0, log_ndtr(-lo), log_ndtr(hi))
        log_lo = np.where(lo > 0, log_ndtr(-hi), log_ndtr(lo))
        numerator = log_hi+np.log(-np.expm1(log_lo-log_hi))
        denominator = log_survival(ages, mu, sigma)
        return -float(np.dot(weights, numerator-denominator))

    candidates = [minimize(lambda z: nll(z[0], math.exp(z[1]), 0.),
                           [alpha, math.log(.6)], method="L-BFGS-B",
                           bounds=((-2., 8.), (-4., 2.))) for alpha in (1., 2., 3.)]
    baseline = min((r for r in candidates if r.success), key=lambda r: r.fun)
    alpha, sigma = float(baseline.x[0]), math.exp(float(baseline.x[1]))
    marked = minimize_scalar(lambda b: nll(alpha, sigma, b), bounds=(0., 5.), method="bounded")
    return {"base_alpha": alpha, "base_sigma": sigma,
            "beta_standardized_log_duration": float(marked.x),
            "gain_nats_per_retained_anchor": float(baseline.fun-marked.fun),
            "baseline_nuisance_fixed": True, "interval_width": .02,
            "scope": "exact weighted late-age counterexample, not an SS Cyg bias estimate"}


def exact_binomial_diagnostics() -> dict:
    n = 40
    # One-sided exact 95% CP upper limits for small rejection counts.
    upper = {
        str(k): (1.0 if k == n else float(beta.ppf(0.95, k + 1, n - k)))
        for k in range(0, 7)
    }
    rejection_tails = {
        str(k): float(binom.sf(k - 1, n, 0.05)) for k in range(1, 8)
    }
    coverage_lower_tails = {
        str(k): float(binom.cdf(k, n, 0.9)) for k in range(28, 37)
    }
    return {
        "n": n,
        "one_sided_95pct_upper_fpr_by_rejections": upper,
        "P_at_least_k_rejections_if_p_0.05": rejection_tails,
        "P_at_most_k_coverages_if_p_0.90": coverage_lower_tails,
        "zero_rejections_upper_bound": upper["0"],
        "minimum_n_zero_rejections_upper_le_0.05": math.ceil(math.log(0.05) / math.log(0.95)),
    }


def main() -> None:
    result = {
        "counterexample": counterexample(),
        "slow_state": partial_correlations(),
        "binomial": exact_binomial_diagnostics(),
    }
    result["fixed_baseline_interval_offset_counterexample"] = offset_counterexample(result["counterexample"]["states"])
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
