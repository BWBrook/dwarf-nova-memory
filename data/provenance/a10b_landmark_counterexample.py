#!/usr/bin/env python3
"""Independent A10 landmark counterexample and Gaussian power check.

No project data are read. The counterexample enumerates a discrete renewal
experiment in which true duration is constant and independent of the next gap,
but duration and landmark age share end-estimation error.
"""

import json
import math
from collections import defaultdict
from pathlib import Path


def entropy(probabilities):
    return -sum(p * math.log(p) for p in probabilities if p > 0)


def normal_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def counterexample():
    # A is true age at issue; eps is estimated-end error, so observed age is
    # A-eps and observed duration is D+eps. Q and true D are independent.
    states = []
    for age in (2.0, 4.0):
        for end_error in (0.0, 2.0):
            for gap in (3.0, 5.0):
                probability = 1.0 / 8.0
                if gap > age:  # same overtaken/survival restriction as a landmark forecast
                    states.append(
                        {
                            "probability_raw": probability,
                            "true_duration": 5.0,
                            "true_age": age,
                            "true_gap": gap,
                            "end_error": end_error,
                            "observed_age": age - end_error,
                            "observed_duration": 5.0 + end_error,
                            "remaining_time": gap - age,
                            "measured_gap": gap - end_error,
                        }
                    )
    retained = sum(row["probability_raw"] for row in states)
    for row in states:
        row["probability"] = row.pop("probability_raw") / retained

    def conditional_entropy(keys, target):
        groups = defaultdict(list)
        for row in states:
            groups[tuple(row[key] for key in keys)].append(row)
        value = 0.0
        details = []
        for key, rows in sorted(groups.items()):
            weight = sum(row["probability"] for row in rows)
            outcomes = defaultdict(float)
            for row in rows:
                outcomes[row[target]] += row["probability"] / weight
            value += weight * entropy(outcomes.values())
            details.append({"stratum": key, "weight": weight,
                            "outcome_probabilities": {str(k): v for k, v in sorted(outcomes.items())}})
        return value, details

    targets = {
        "true_gap_Q": "true_gap",
        "remaining_time_R_equals_Q_minus_A": "remaining_time",
        "measured_gap_Qhat_equals_Q_minus_end_error": "measured_gap",
    }
    gains = {}
    for label, target in targets.items():
        h_age, by_age = conditional_entropy(("observed_age",), target)
        h_mark, by_age_mark = conditional_entropy(("observed_age", "observed_duration"), target)
        gains[label] = {
            "baseline_conditional_entropy_nats": h_age,
            "mark_model_conditional_entropy_nats": h_mark,
            "oracle_expected_log_score_gain_nats": h_age - h_mark,
            "baseline_strata": by_age,
            "mark_strata": by_age_mark,
        }
    return {
        "data_generating_null": "true duration is constant; Q is sampled independently of duration",
        "retained_probability_after_issue_before_onset": retained,
        "target_definitions": {
            "true_gap_Q": "true next-onset time minus true current end",
            "remaining_time_R_equals_Q_minus_A": "true next-onset time minus issue time",
            "measured_gap_Qhat_equals_Q_minus_end_error": "true next-onset time minus estimated current end",
        },
        "gains_by_target": gains,
        "states": states,
    }


def gaussian_power(r=0.12, n=390, alpha=0.05):
    # 1.6448536269514722 is the one-sided 95% standard-normal quantile.
    critical = 1.6448536269514722
    ideal_gain = -0.5 * math.log1p(-(r * r))
    # For oracle bivariate Gaussian conditional vs marginal forecasts,
    # Var(per-case log-score difference) = r^2 exactly.
    score_noncentrality = ideal_gain * math.sqrt(n) / abs(r)
    slope_noncentrality = r * math.sqrt((n - 2.0) / (1.0 - r * r))
    return {
        "r": r,
        "n": n,
        "one_sided_alpha": alpha,
        "ideal_gain_nats": ideal_gain,
        "exact_oracle_score_sd_per_case": abs(r),
        "score_noncentrality_normal_approx": score_noncentrality,
        "score_power_normal_approx": normal_cdf(score_noncentrality - critical),
        "slope_noncentrality_normal_approx": slope_noncentrality,
        "slope_power_normal_approx": normal_cdf(slope_noncentrality - critical),
        "interpretation": {
            "score": "tests positive out-of-sample expected log-score gain for frozen forecasts",
            "slope": "tests a positive association after estimating the slope from evaluation outcomes",
        },
    }


def main():
    result = {"counterexample": counterexample(), "gaussian_power": gaussian_power()}
    output = Path(__file__).with_name("a10b_landmark_counterexample.json")
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
