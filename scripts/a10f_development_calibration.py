"""Place the real 1910-1959 development fit within the A10d synthetic development fits.

Reads the 360 per-trial A10d results (archive a10d-20261108-8f5df44, outside Git),
the committed A10e summary, and the real development ledger (archive
a10e-20261108-b80c4a9, outside Git; pre-1960 rows only). Writes a compact JSON.
Nothing here touches 1960+ data or changes the frozen forecast system.
"""

import argparse
from collections import defaultdict
import glob
import hashlib
import json
from pathlib import Path
import statistics

from scipy.stats import beta as beta_dist


def exact(successes, trials):
    lo = 0.0 if successes == 0 else beta_dist.ppf(.025, successes, trials - successes + 1)
    hi = 1.0 if successes == trials else beta_dist.ppf(.975, successes + 1, trials - successes)
    up = 1.0 if successes == trials else beta_dist.ppf(.95, successes + 1, trials - successes)
    return {'successes': successes, 'trials': trials, 'rate': successes/trials,
            'exact_95': [float(lo), float(hi)], 'one_sided_upper_95': float(up)}


def trial_record(path):
    r = json.loads(Path(path).read_text())['result']
    models = r['models']['primary']['models']
    m3, p3 = models['M3']['metadata'], models['P3']['metadata']
    best = min([s['objective'] for s in m3['successful_starts']] + [m3['selected_zero_objective']])
    six = r['intervals']['primary']['6']
    return {'family': r['family'], 'case': r['case'], 'replicate': r['replicate'],
            'beta': m3['beta'][0], 'lag_beta': p3['beta'][0],
            'joint_lag_beta': r['models']['joint_placebo']['models']['P3']['metadata']['beta'][0],
            'dev_lr': 2*(m3['selected_zero_objective'] - best),
            'q_slope': models['M2']['coefficients']['previous_gap'],
            'local_slope': models['M2']['coefficients']['earlier_level'],
            'sigma': models['M2']['sigma'], 'mark_scale': models['M3']['scales']['mark'],
            'training_issued': r['counts']['training_issued'],
            'heldout_gain': six['gain_M3_M2']['estimate'], 'confirmed': six['gain_M3_M2']['confirmed']}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--oc', default='outputs/a10d_run_8f5df44/a10d_oc')
    p.add_argument('--real-summary', default='data/fits/a10e_1910_1959/summary.json')
    p.add_argument('--real-parameters', default='data/fits/a10e_1910_1959/frozen_parameters.json')
    p.add_argument('--real-ledger', default='outputs/a10e_development_b80c4a9/ledger-0.0.json')
    p.add_argument('--output', default='data/simulations/a10f_development_calibration_20261108.json')
    a = p.parse_args()

    paths = sorted(glob.glob(f'{a.oc}/*-[0-9][0-9][0-9].json'))
    if len(paths) != 360:
        raise SystemExit(f'expected 360 trial files, found {len(paths)}')
    receipt_sha = hashlib.sha256(Path(a.oc, 'receipt.json').read_bytes()).hexdigest()
    trials = [trial_record(x) for x in paths]

    summary = json.loads(Path(a.real_summary).read_text())['primary']
    params = json.loads(Path(a.real_parameters).read_text())['primary']['models']
    ll = summary['log_likelihood']
    real = {'beta': params['M3']['coefficients']['beta'], 'lag_beta': params['P3']['coefficients']['beta'],
            'dev_lr': 2*(ll['M3'] - ll['M2']), 'scored': summary['scored'],
            'q_slope': params['M2']['coefficients']['previous_gap'],
            'local_slope': params['M2']['coefficients']['earlier_level'],
            'sigma': params['M2']['sigma'], 'mark_scale': params['M3']['scales']['mark']}

    ledger = json.loads(Path(a.real_ledger).read_text())
    ages = sorted(f['age_at_issue'] for f in ledger if f.get('age_at_issue') is not None)
    gaps = sorted(f['previous_gap'] for f in ledger if f.get('previous_gap'))
    q = lambda v, pr: v[round(pr*(len(v) - 1))]
    issue_ages = {'n': len(ages), 'median_d': q(ages, .5), 'p90_d': q(ages, .9), 'max_d': ages[-1],
                  'over_10_d': sum(x > 10 for x in ages),
                  'previous_gap_median_d': q(gaps, .5), 'previous_gap_p10_d': q(gaps, .1)}

    groups = defaultdict(list)
    for t in trials:
        groups[(t['family'], t['case'])].append(t)
    cases = []
    for (family, case), v in sorted(groups.items()):
        strong = [t for t in v if t['dev_lr'] >= real['dev_lr']]
        moderate = [t for t in v if t['dev_lr'] >= 2.706]
        cases.append({
            'family': family, 'case': case, 'trials': len(v),
            'dev_lr_at_least_real': len([t for t in v if t['dev_lr'] >= real['dev_lr']]),
            'beta_at_least_real': len([t for t in v if t['beta'] >= real['beta']]),
            'lag_beta_zero': len([t for t in v if t['lag_beta'] == 0]),
            'q_slope_mean_sd': [statistics.fmean(t['q_slope'] for t in v), statistics.stdev(t['q_slope'] for t in v)],
            'local_slope_mean_sd': [statistics.fmean(t['local_slope'] for t in v), statistics.stdev(t['local_slope'] for t in v)],
            'sigma_mean': statistics.fmean(t['sigma'] for t in v),
            'mark_scale_mean': statistics.fmean(t['mark_scale'] for t in v),
            'training_issued_mean': statistics.fmean(t['training_issued'] for t in v),
            'dev_lr_ge_2.706': {'trials': len(moderate), 'lag_beta_zero': sum(t['lag_beta'] == 0 for t in moderate),
                                'confirmed': sum(t['confirmed'] for t in moderate)},
            'dev_lr_ge_real': {'trials': len(strong), 'lag_beta_zero': sum(t['lag_beta'] == 0 for t in strong),
                               'confirmed': sum(t['confirmed'] for t in strong),
                               'mean_heldout_gain': statistics.fmean(t['heldout_gain'] for t in strong) if strong else None}})

    gated = {('v2-phase', c) for c in ('null', 'structured', 'gross', 'offset', 'adaptive')} | {('v4-phase', 'null')}
    gated_trials = [t for t in trials if (t['family'], t['case']) in gated]
    slow = [t for t in trials if t['case'] in ('slow_090', 'slow_098')]
    alt = [t for t in trials if (t['family'], t['case']) == ('v2-phase', 'alternative')]
    pooled = {
        'gated_null_dev_lr_at_least_real': exact(sum(t['dev_lr'] >= real['dev_lr'] for t in gated_trials), len(gated_trials)),
        'gated_null_confirmations': exact(sum(t['confirmed'] for t in gated_trials), len(gated_trials)),
        'lag_zero_given_dev_lr_ge_2.706': {
            'v2_alternative': exact(sum(t['lag_beta'] == 0 for t in alt if t['dev_lr'] >= 2.706), sum(t['dev_lr'] >= 2.706 for t in alt)),
            'v2_slow_state': exact(sum(t['lag_beta'] == 0 for t in slow if t['dev_lr'] >= 2.706), sum(t['dev_lr'] >= 2.706 for t in slow))},
        'confirmed_given_dev_lr_ge_real': {
            'v2_alternative': exact(sum(t['confirmed'] for t in alt if t['dev_lr'] >= real['dev_lr']), sum(t['dev_lr'] >= real['dev_lr'] for t in alt))},
        'note': 'gated null cases share random streams (null/gross/offset/adaptive), so pooled intervals understate uncertainty'}

    out = {'scope': 'development-stage calibration of the real 1910-1959 fit against A10d synthetic development fits; no 1960+ data',
           'a10d_receipt_sha256': receipt_sha, 'real': real, 'real_issue_ages': issue_ages,
           'cases': cases, 'pooled': pooled}
    Path(a.output).write_text(json.dumps(out, indent=1, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
