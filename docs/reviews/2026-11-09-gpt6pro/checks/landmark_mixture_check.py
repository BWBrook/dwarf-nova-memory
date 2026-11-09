#!/usr/bin/env python3
"""Synthetic check of landmark mixture probabilities and matched fallback routing."""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True
import argparse
from dataclasses import replace
import math
from pathlib import Path
from statistics import NormalDist

from _review_support import (COMMIT, environment, load_verified_module, require,
                             verify_repo, write_output)


def cdf(time: float, mu: float, sigma: float) -> float:
    return 0.0 if time <= 0.0 else NormalDist(mu, sigma).cdf(math.log(time))


def expected(feature: dict, outcome: dict, endpoints: list[float], beta: float) -> tuple[float, float]:
    numerators, denominators = [], []
    for end in endpoints:
        duration = end - feature['onset_t']
        mu = math.log(10.0) + beta * (math.log(duration) - math.log(10.0)) / 0.3
        denominators.append(1.0 - cdf(feature['issue_time'] - end, mu, 0.5))
        if outcome['kind'] == 'interval':
            numerators.append(cdf(outcome['onset_hi'] - end, mu, 0.5)
                              - cdf(outcome['onset_lo'] - end, mu, 0.5))
        else:
            numerators.append(1.0 - cdf(outcome['censor_at'] - end, mu, 0.5))
    mixture_then_condition = math.log(math.fsum(numerators) / math.fsum(denominators))
    condition_then_average = math.log(math.fsum(n / d for n, d in zip(numerators, denominators)) / len(endpoints))
    return mixture_then_condition, condition_then_average


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True, help='Local checkout containing the exact pinned reviewed source files.')
    parser.add_argument('--output', type=Path, required=True, help='JSON output outside the checkout; parent must exist.')
    args = parser.parse_args()
    repo = args.repo.expanduser().resolve(strict=True)
    names = ('src/dnmem/__init__.py', 'src/dnmem/ledger_forecast.py', 'src/dnmem/directional_forecast.py')
    checked = verify_repo(repo, names)
    # Explicit import origins: no installed dnmem package, no repository pipeline.
    load_verified_module('dnmem', repo / names[0], package=True)
    ledger = load_verified_module('dnmem.ledger_forecast', repo / names[1])
    directional = load_verified_module('dnmem.directional_forecast', repo / names[2])
    ForecastModel, DirectionalBundle = ledger.ForecastModel, directional.DirectionalBundle

    def model(name: str, beta: float | None = None):
        coefficients = {} if name in ('M0', 'R0') else {'previous_gap': 0.0, 'earlier_level': 0.0}
        centers = {'previous_gap': math.log(10.0), 'earlier_level': math.log(10.0)}
        scales = {'previous_gap': 1.0, 'earlier_level': 1.0}
        if beta is not None:
            coefficients['beta'] = beta
            centers['mark'], scales['mark'] = math.log(10.0), 0.3
        return ForecastModel(name, math.log(10.0), coefficients, 0.5, centers, scales,
                             100, tuple(coefficients), {'synthetic_review_fixture': True})

    feature = {'emission_index': 0, 'issue_time': 6.0, 'onset_t': -8.0,
               'end_t': 2.0, 'end_lo': 0.0, 'end_hi': 4.0, 'duration': 10.0,
               'landmark_available': True, 'previous_gap_covered': True,
               'previous_gap': 10.0, 'previous_duration': 10.0,
               'earlier_gaps': [math.log(10.0)] * 6}
    outcomes = [
        {'emission_index': 0, 'issue_time': 6.0, 'kind': 'interval', 'onset_lo': 8.0, 'onset_hi': 12.0},
        {'emission_index': 0, 'issue_time': 6.0, 'kind': 'right_censored', 'censor_at': 10.0}]
    rows, bundles = [], {}
    for mode, endpoints in (('point', [2.0]), ('uniform_end', [0.0, 1.0, 2.0, 3.0, 4.0])):
        bundle = DirectionalBundle(
            models={'M0': model('M0'), 'M2': model('M2'), 'M3': model('M3', 0.15), 'P3': model('P3', 0.0)},
            r0=model('R0'), endpoint_mode=mode, nodes=5, mark_mode='log_duration',
            local_level=True, directional=True, joint_marks=False, counts={}, metadata={})
        bundles[mode] = bundle
        for name, beta in (('M0', 0.0), ('M2', 0.0), ('M3', 0.15)):
            for outcome in outcomes:
                actual = bundle.score(feature, outcome, name)
                target, alternative = expected(feature, outcome, endpoints, beta)
                require(actual is not None and abs(actual - target) < 1e-12,
                        f'Landmark probability mismatch for {mode}, {name}, {outcome["kind"]}.')
                rows.append({'mode': mode, 'model': name, 'outcome': outcome['kind'],
                             'repository_log_score': actual, 'independent_log_score': target,
                             'absolute_difference': abs(actual - target),
                             'unweighted_average_of_conditional_ratios': alternative})
    routing = []
    bundle = bundles['point']
    for label, altered in (('missing_previous_gap', dict(feature, previous_gap_covered=False)),
                           ('missing_landmark', dict(feature, landmark_available=False)),
                           ('invalid_duration', dict(feature, onset_t=2.0))):
        scores = [bundle.score(altered, outcomes[0], name) for name in ('M2', 'M3')]
        require(scores[0] is not None and scores[1] == scores[0], f'Unequal fallback: {label}')
        routing.append({'case': label, 'M2_route': bundle.route(altered, 'M2'),
                        'M3_route': bundle.route(altered, 'M3'), 'paired_gain': scores[1] - scores[0]})
    zero_models = dict(bundle.models)
    zero_models['M3'] = model('M3', 0.0)
    zero_bundle = replace(bundle, models=zero_models)
    require(zero_bundle.route(feature, 'M3') == 'M2', 'Zero-beta model does not route to M2.')
    require(zero_bundle.score(feature, outcomes[0], 'M3') == zero_bundle.score(feature, outcomes[0], 'M2'),
            'Zero-beta score differs from M2.')
    routing.append({'case': 'zero_beta', 'M2_route': 'M2', 'M3_route': 'M2', 'paired_gain': 0.0})
    payload = {
        'scope': 'Synthetic selected-path arithmetic check; no archival observations, fitted primary outcomes, or pipeline execution.',
        'reviewed_commit': COMMIT, 'environment': environment(), 'checked_repository_sources': checked,
        'feature_fixture': feature, 'outcome_fixtures': outcomes,
        'probability_checks': rows, 'routing_checks': routing,
        'maximum_log_difference': max(r['absolute_difference'] for r in rows),
        'limits': ['For uncertain endpoints, verifies log(sum numerator / sum survival), not an average of conditional ratios.',
                   'This checks the implemented working likelihood on one deterministic fixture, not its physical validity or score propriety.',
                   'Does not reproduce extraction, acquisition, development fitting, any real forecast, or the primary result.',
                   'Does not validate the endpoint mixture distribution or complete propagation of measurement uncertainty.']}
    write_output(args.output, payload, repo)


if __name__ == '__main__':
    main()
