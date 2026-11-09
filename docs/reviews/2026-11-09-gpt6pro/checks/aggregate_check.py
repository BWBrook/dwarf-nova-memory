#!/usr/bin/env python3
"""Recompute declared aggregate statistics from ten public block summaries."""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True
import argparse
import json
import math
from pathlib import Path

from scipy.stats import t
from _review_support import COMMIT, environment, public_input, require, verify_repo, write_output


def summary(blocks: list[dict]) -> dict:
    n = sum(b['n'] for b in blocks)
    g = len(blocks)
    mean = math.fsum(b['n'] * b['mean_gain'] for b in blocks) / n
    residual_sums = [b['n'] * (b['mean_gain'] - mean) for b in blocks]
    variance = (g / (g - 1)) * math.fsum(u * u for u in residual_sums) / (n * n)
    se = math.sqrt(variance)
    critical = float(t.ppf(0.95, g - 1))
    return {'n': n, 'clusters': g, 'degrees_of_freedom': g - 1,
            'weighted_mean_gain_nats': mean, 'CR1_standard_error': se,
            't_0_95': critical, 'two_sided_90_percent_interval': [mean - critical * se, mean + critical * se],
            'one_sided_95_percent_lower_bound': mean - critical * se,
            'geometric_mean_mass_ratio': math.exp(mean),
            'geometric_mean_mass_change_percent': 100 * math.expm1(mean)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, help='Optional local pinned checkout: verify original public figure input.')
    parser.add_argument('--output', type=Path, required=True, help='JSON output; parent directory must already exist.')
    args = parser.parse_args()
    inputs, input_hash = public_input()
    blocks = inputs['blocks']
    require([b['block'] for b in blocks] == list(range(10)), 'Expected the ten ordered reviewed blocks.')
    require(all(isinstance(b['n'], int) and b['n'] > 0 and math.isfinite(b['mean_gain']) for b in blocks),
            'Invalid aggregate counts or means.')
    checked = {}
    if args.repo is not None:
        name = 'manuscript/figure-data/fig2-gains.json'
        checked = verify_repo(args.repo, (name,))
        original = json.loads((args.repo.expanduser().resolve() / name).read_text())
        extracted = [{k: b[k] for k in ('block', 'n', 'mean_gain')} for b in original['blocks']]
        require(extracted == blocks, 'Bundled counts/means differ from the pinned original.')
    primary = summary(blocks)
    reference = inputs['reported_primary']
    require(primary['n'] == reference['n'], 'Total count does not reproduce the public primary.')
    discrepancies = {
        'mean': abs(primary['weighted_mean_gain_nats'] - reference['estimate']),
        'lower': abs(primary['two_sided_90_percent_interval'][0] - reference['lower']),
        'upper': abs(primary['two_sided_90_percent_interval'][1] - reference['upper'])}
    require(max(discrepancies.values()) < 1e-12, 'Aggregate primary/interval does not reproduce the reported values.')
    loo = [{'omitted_block': b['block'],
            'weighted_mean_gain_nats': summary([x for x in blocks if x is not b])['weighted_mean_gain_nats']}
           for b in blocks]
    # Exactly one fixed post-result grouping: (0,1), (2,3), (4,5), (6,7), (8,9).
    # No alternative widths, offsets, or choices are searched.
    paired = []
    for start in range(0, 10, 2):
        pair = blocks[start:start + 2]
        total = sum(b['n'] for b in pair)
        paired.append({'members': [b['block'] for b in pair], 'n': total,
                       'mean_gain': math.fsum(b['n'] * b['mean_gain'] for b in pair) / total})
    payload = {
        'scope': 'Public aggregate arithmetic only; no observations, per-forecast scores, or archive access.',
        'reviewed_commit': COMMIT, 'environment': environment(),
        'input_sha256': input_hash, 'checked_repository_sources': checked,
        'formula': 'mean=sum(n_g*m_g)/N; SE^2=(G/(G-1))*sum([n_g*(m_g-mean)]^2)/N^2; interval=mean +/- t_(.95,G-1)*SE',
        'primary_six_year_blocks': primary, 'reference_absolute_discrepancies': discrepancies,
        'positive_block_means': sum(b['mean_gain'] > 0 for b in blocks),
        'leave_one_block_out': loo,
        'leave_one_block_out_mean_range': [min(x['weighted_mean_gain_nats'] for x in loo), max(x['weighted_mean_gain_nats'] for x in loo)],
        'single_exploratory_adjacent_pair_grouping': {'status': 'Post-result review sensitivity; not predeclared confirmation.',
            'grouping': paired, 'statistics': summary(paired),
            'calendar_note': 'Nominal 12-year groups; the final group spans the shorter terminal block. Uses five clusters and t4.'},
        'limits': ['Assumes public counts and block means are correct; does not reproduce individual scores.',
                   'CR1 arithmetic does not establish cluster independence or valid interval coverage.',
                   'Coarser grouping is one exploratory diagnostic, not a tuned or replacement primary interval.',
                   'The exponential is a geometric bracket-mass ratio, not accuracy, variance explained, or a physical effect.']}
    write_output(args.output, payload, args.repo)


if __name__ == '__main__':
    main()
