#!/usr/bin/env python3
"""Independent finite-state demonstration of positive information from endpoint error."""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True
import argparse
from fractions import Fraction
import itertools
import math
from pathlib import Path

from scipy.optimize import minimize, minimize_scalar
from _review_support import (COMMIT, environment, load_verified_module, require,
                             verify_repo, write_output)


def sf(time: float, mu: float, sigma: float) -> float:
    return 1.0 if time <= 0.0 else 0.5 * math.erfc((math.log(time) - mu) / (sigma * math.sqrt(2.0)))


def interval(lo: float, hi: float, mu: float, sigma: float) -> float:
    if math.log(lo) >= mu:
        return sf(lo, mu, sigma) - sf(hi, mu, sigma)
    return 0.5 * (math.erfc(-(math.log(hi) - mu) / (sigma * math.sqrt(2.0)))
                  - math.erfc(-(math.log(lo) - mu) / (sigma * math.sqrt(2.0))))


def calculate() -> dict:
    states = []
    for age, error, (gap, probability) in itertools.product(
            (2, 8), (0, 6), ((5, Fraction(9, 10)), (20, Fraction(1, 10)))):
        if age - error >= 0 and gap > age:
            states.append({'true_age': age, 'end_error': error, 'true_duration': 10,
                           'true_gap': gap, 'observed_age': age - error,
                           'observed_duration': 10 + error, 'observed_gap': gap - error,
                           'remaining': gap - age, 'probability': probability / 4})
    total = sum(s['probability'] for s in states)
    for state in states:
        state['weight'] = state['probability'] / total
    means = {}
    for duration in (10, 16):
        selected = [s for s in states if s['observed_age'] == 2 and s['observed_duration'] == duration]
        means[str(duration)] = float(sum(s['weight'] * s['remaining'] for s in selected)
                                    / sum(s['weight'] for s in selected))
    require(means == {'10': 4.5, '16': 12.0}, 'Exact finite-state conditional means differ.')
    at_two = [s for s in states if s['observed_age'] == 2]
    p_high = (sum(s['weight'] for s in at_two if s['observed_duration'] == 16)
              / sum(s['weight'] for s in at_two))
    require(p_high == Fraction(1, 11), 'Exact conditional class probability differs.')
    # At observed age two the two duration groups have disjoint remaining-time supports.
    information = -float(p_high) * math.log(float(p_high)) - float(1 - p_high) * math.log(float(1 - p_high))
    center = math.fsum(float(s['weight']) * math.log(s['observed_duration']) for s in states)
    scale = math.sqrt(math.fsum(float(s['weight']) * (math.log(s['observed_duration']) - center) ** 2 for s in states))

    def nll(alpha: float, log_sigma: float, coefficient: float) -> float:
        sigma = math.exp(log_sigma)
        values = []
        for state in states:
            x = (math.log(state['observed_duration']) - center) / scale
            mu = alpha + coefficient * x
            numerator = interval(state['observed_gap'] - 0.01, state['observed_gap'] + 0.01, mu, sigma)
            denominator = sf(state['observed_age'], mu, sigma)
            if numerator <= 0.0 or denominator <= 0.0:
                return 1e100
            values.append(float(state['weight']) * (math.log(numerator) - math.log(denominator)))
        return -math.fsum(values)

    fits = [minimize(lambda p: nll(p[0], p[1], 0.0), (math.log(median), math.log(sigma)),
                     method='Powell', bounds=((-2.0, 8.0), (-4.0, 2.0)),
                     options={'xtol': 1e-10, 'ftol': 1e-12})
            for median, sigma in itertools.product((5, 10, 20), (0.3, 0.8, 1.5))]
    successful = [fit for fit in fits if fit.success and math.isfinite(fit.fun) and fit.fun < 1e99]
    require(bool(successful), 'Independent baseline optimization failed.')
    baseline = min(successful, key=lambda fit: fit.fun)
    marked = minimize_scalar(lambda b: nll(baseline.x[0], baseline.x[1], b),
                              bounds=(0.0, 5.0), method='bounded', options={'xatol': 1e-10})
    gain = float(baseline.fun - marked.fun)
    require(marked.success and marked.x > 0.0 and gain > 0.0, 'Positive-offset counterexample was not reproduced.')
    serial_states = [{k: (str(v) if isinstance(v, Fraction) else v) for k, v in state.items()} for state in states]
    return {'states': serial_states, 'retention_probability': str(total),
            'mean_remaining_by_observed_duration_at_observed_age_2': means,
            'conditional_high_duration_probability': str(p_high),
            'mutual_information_nats_at_observed_age_2': information,
            'independent_fixed_baseline_fit': {'alpha': float(baseline.x[0]),
                'sigma': math.exp(float(baseline.x[1])), 'beta': float(marked.x), 'gain_nats': gain,
                'mark_center': center, 'mark_scale': scale, 'interval_width': 0.02,
                'successful_baseline_starts': len(successful), 'total_baseline_starts': len(fits),
                'baseline_optimizer': 'Powell', 'mark_optimizer': 'bounded scalar'}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, help='Optional pinned local checkout; compare helper only after independent calculation.')
    parser.add_argument('--output', type=Path, required=True, help='JSON output; parent directory must already exist.')
    args = parser.parse_args()
    # Independent enumeration and fitting happen before any optional repository read/import.
    result = calculate()
    checked, comparison = {}, {'performed': False}
    if args.repo is not None:
        repo = args.repo.expanduser().resolve(strict=True)
        name = 'scripts/a10d_design_calculations.py'
        checked = verify_repo(repo, (name,))
        helper = load_verified_module('pinned_review_design_calculation', repo / name)
        original = helper.counterexample()
        offset = helper.offset_counterexample(original['states'])
        independent = result['independent_fixed_baseline_fit']
        differences = {'mutual_information': abs(result['mutual_information_nats_at_observed_age_2'] - original['mutual_information_nats_at_ahat_2']),
                       'beta': abs(independent['beta'] - offset['beta_standardized_log_duration']),
                       'gain_nats': abs(independent['gain_nats'] - offset['gain_nats_per_retained_anchor'])}
        require(differences['mutual_information'] < 1e-12 and differences['beta'] < 1e-4 and differences['gain_nats'] < 1e-7,
                f'Optional helper cross-check differs: {differences}')
        comparison = {'performed': True, 'absolute_differences': differences,
                      'tolerances': {'mutual_information': 1e-12, 'beta': 1e-4, 'gain_nats': 1e-7},
                      'helper_fixed_baseline_fit': offset,
                      'note': 'Helper called only after independent fit; its main/write entry point is not called.'}
    payload = {'scope': 'Synthetic finite-state counterexample; no repository needed for the independent result.',
               'reviewed_commit_context': COMMIT, 'environment': environment(),
               'construction': 'Independent equiprobable true ages {2,8} and end errors {0,6}; true duration 10; gap 5 with probability .9 or 20 with .1. Retain observed age >=0 and true gap > true age.',
               **result, 'checked_repository_sources': checked, 'optional_repository_crosscheck': comparison,
               'limits': ['Existence demonstration only; does not estimate the size or sign of SS Cyg measurement bias.',
                          'Exact finite-state weights are not sampled archive observations; optimization is numerical.',
                          'A nonnegative duration coefficient cannot universally exclude endpoint-error information.',
                          'Passing this check does not identify the cause of the manuscript score gain.']}
    write_output(args.output, payload, args.repo)


if __name__ == '__main__':
    main()
