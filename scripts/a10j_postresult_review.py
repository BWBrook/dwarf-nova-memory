"""Claude's post-result review of the sealed SS Cyg 1960-2017 comparison (A10j).

EXPLORATORY AND POST-RESULT. Everything here was computed after the A10i primary
result existed. It re-reads the saved evaluation outputs (outside Git) and the
pre-1960 development ledger, and writes aggregates only. None of it can become a
second confirmation, alter the frozen comparison, or justify a 2018+ request.

Three parts:
1. An interval recomputation from the saved per-issuance gains with separate code
   (the frozen interval module is not imported), plus block-level influence.
2. Level-versus-slope decomposition of the frozen M3-M2 gain.
3. Type versus within-type information with the frozen M2 nuisance held fixed,
   and duration alternation.
Scores are recomputed with the independent checker's scalar score function.
"""

import argparse
import copy
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import sys

from scipy.optimize import minimize, minimize_scalar
from scipy.stats import t as tdist

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_a10d_scores import conditional_score, current_durations, endpoint_nodes  # noqa: E402

START, END, SPLIT = 2436934.5, 2458119.5, 2448988.5
ERAS = {'1960-2017': (START, END), '1960-1992': (START, SPLIT), '1993-2017': (SPLIT, END)}
TYPE_SPLIT_D = 12.0
NM = {'xatol': 1e-7, 'fatol': 1e-9, 'maxiter': 4000}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cluster(vals, times, origin, years=6, factor=True):
    n = len(vals)
    m = sum(vals) / n
    g = defaultdict(float)
    for v, t in zip(vals, times):
        g[int((t - origin) // (years * 365.25))] += v - m
    k = len(g)
    se = math.sqrt((k / (k - 1) if factor else 1.0) * sum(x * x for x in g.values())) / n
    q = tdist.ppf(.95, k - 1)
    return {'n': n, 'estimate': m, 'se': se, 'blocks': k, 'df': k - 1,
            'lower_90': m - q * se, 'upper_90': m + q * se}


def era_stat(rows, gain):
    out = {}
    for era, (lo, hi) in ERAS.items():
        sub = [r for r in rows if lo <= r['issue_time'] < hi]
        out[era] = cluster([gain[r['emission_index']] for r in sub], [r['issue_time'] for r in sub], lo)
    return out


class Scorer:
    def __init__(self, spec, ledger, evidence, rows):
        self.spec, self.led, self.ev = spec, ledger, evidence
        self.timing = [r for r in rows if r['M3_route'] == 'M3']

    def scores(self, route, over):
        sp = copy.deepcopy(self.spec)
        sp['models'][route].update(over)
        return {r['emission_index']: conditional_score(self.led[r['emission_index']], self.ev[r['emission_index']], sp, route)
                for r in self.timing}

    def nll(self, route, over):
        return -sum(self.scores(route, over).values())


def type_refits(params, led, ev, prim_rows, type_rows, eras):
    """Frozen M2 nuisance, free common level: raw log duration, type only, type plus within-type."""
    ps, ts = params['primary'], params['type_within']
    S, T = Scorer(ps, led, ev, prim_rows), Scorer(ts, led, ev, type_rows)
    m2, m3, m3t = ps['models']['M2'], ps['models']['M3'], ts['models']['M3']
    refits = {}
    for era, (lo, hi) in eras.items():
        def sub(scorer):
            q = copy.copy(scorer)
            q.timing = [r for r in scorer.timing if lo <= r['issue_time'] < hi]
            return q
        Se, Te = sub(S), sub(T)
        f0 = minimize(lambda v: Se.nll('M2', {'intercept': m2['intercept'] + v[0]}), [0.0], method='Nelder-Mead', options=NM)
        fr = minimize(lambda v: Se.nll('M3', {'intercept': m3['intercept'] + v[0], 'coefficients': {**m3['coefficients'], 'beta': v[1]}}),
                      [f0.x[0], .05], method='Nelder-Mead', options=NM)
        ft = minimize(lambda v: Te.nll('M3', {'intercept': m3t['intercept'] + v[0],
                                              'coefficients': {**m3t['coefficients'], 'beta_type': v[1], 'beta_within': 0.0}}),
                      [f0.x[0], .05], method='Nelder-Mead', options=NM)
        ftw = minimize(lambda v: Te.nll('M3', {'intercept': m3t['intercept'] + v[0],
                                               'coefficients': {**m3t['coefficients'], 'beta_type': v[1], 'beta_within': v[2]}}),
                       [ft.x[0], ft.x[1], 0.0], method='Nelder-Mead', options=NM)
        refits[era] = {
            'n_timing': len(Se.timing),
            'level_only_shift': f0.x[0],
            'raw_log_duration': {'level_shift': fr.x[0], 'beta_per_training_sd': fr.x[1], 'lr_vs_level_only': 2 * (f0.fun - fr.fun)},
            'type_only': {'level_shift': ft.x[0], 'beta_type_long_minus_short': ft.x[1], 'lr_vs_level_only': 2 * (f0.fun - ft.fun)},
            'type_plus_within': {'level_shift': ftw.x[0], 'beta_type_long_minus_short': ftw.x[1],
                                 'beta_within_per_frozen_within_sd': ftw.x[2],
                                 'lr_within_given_type': 2 * (ft.fun - ftw.fun), 'lr_vs_level_only': 2 * (f0.fun - ftw.fun)},
            'lr_type_only_minus_raw_log_duration': 2 * (fr.fun - ft.fun)}
    return refits


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run', default='outputs/a10h_live_repair_5e39aeb')
    p.add_argument('--committed-primary', default='data/provenance/a10i_evaluation_1960_2017/primary.json')
    p.add_argument('--dev-ledger', default='outputs/a10e_development_b80c4a9/ledger-0.0.json')
    p.add_argument('--output', default='data/provenance/a10j_postresult_review/summary.json')
    a = p.parse_args()
    run = Path(a.run)
    inputs = {name: str(run / name) for name in
              ('frozen_parameters.json', 'ledger-0.0.json', 'evidence-0.0.json', 'primary-scores.json', 'type_within-scores.json')}
    inputs['committed_primary'] = a.committed_primary
    inputs['development_ledger'] = a.dev_ledger
    for v in ('uniform_end', 'q_only', 'delay_2', 'joint_placebo'):
        inputs[f'{v}-scores.json'] = str(run / f'{v}-scores.json')
    for name in ('frozen_parameters.json', 'evidence-0.0.json', 'primary-scores.json', 'type_within-scores.json'):
        inputs['development_' + name] = str(Path(a.dev_ledger).parent / name)
    params = json.loads((run / 'frozen_parameters.json').read_text())
    led = {r['emission_index']: r for r in json.loads((run / 'ledger-0.0.json').read_text())}
    ev = {r['emission_index']: r for r in json.loads((run / 'evidence-0.0.json').read_text())}
    prim_rows = json.loads((run / 'primary-scores.json').read_text())
    type_rows = json.loads((run / 'type_within-scores.json').read_text())
    committed = json.loads(Path(a.committed_primary).read_text())

    # 1. Interval recomputation and influence.
    gains = {r['emission_index']: r['gain_M3_M2'] for r in prim_rows}
    times = [r['issue_time'] for r in prim_rows]
    vals = [r['gain_M3_M2'] for r in prim_rows]
    cr1 = cluster(vals, times, START)
    cr0 = cluster(vals, times, START, factor=False)
    q9 = tdist.ppf(.95, cr1['df'])
    blocks = defaultdict(list)
    for r in prim_rows:
        blocks[int((r['issue_time'] - START) // (6 * 365.25))].append(r['gain_M3_M2'])
    block_rows = []
    for k, v in sorted(blocks.items()):
        rest = [x for kk, vv in blocks.items() if kk != k for x in vv]
        block_rows.append({'block': k, 'start_year': 1960 + 6 * k, 'n': len(v), 'mean_gain': sum(v) / len(v),
                           'mean_gain_without_block': sum(rest) / len(rest)})
    srt = sorted(vals)
    recompute = {
        'method': 'CR1 cluster-robust mean, G/(G-1) factor, Student t with G-1 df; separate code from the frozen interval module',
        'cr1': cr1, 'cr0_no_small_sample_factor': cr0,
        'matches_committed_primary': all(abs(cr1[k] - committed[c]) < 1e-12 for k, c in
                                         (('estimate', 'estimate'), ('se', 'se'), ('lower_90', 'lower'), ('upper_90', 'upper'))),
        'se_inflation_tolerated_before_rule_fails': cr1['estimate'] / (q9 * cr1['se']),
        'blocks': block_rows, 'blocks_positive': sum(b['mean_gain'] > 0 for b in block_rows),
        'leave_one_block_out_range': [min(b['mean_gain_without_block'] for b in block_rows),
                                      max(b['mean_gain_without_block'] for b in block_rows)],
        'issuance_share_positive': sum(x > 0 for x in vals) / len(vals), 'issuance_median_gain': srt[len(srt) // 2],
        'eras': era_stat(prim_rows, gains),
        'three_year_clusters': cluster(vals, times, START, years=3)}
    variant_rows = {v: json.loads((run / f'{v}-scores.json').read_text())
                    for v in ('primary', 'uniform_end', 'q_only', 'delay_2', 'joint_placebo', 'type_within')}
    recompute['variant_gains_M3_minus_M2'] = {v: cluster([r['gain_M3_M2'] for r in rs], [r['issue_time'] for r in rs], START)
                                             for v, rs in variant_rows.items()}
    recompute['primary_gain_M2_minus_M0'] = cluster([r['gain_M2_M0'] for r in prim_rows], times, START)

    # 2. Level versus slope.
    ps = params['primary']
    S = Scorer(ps, led, ev, prim_rows)
    m2, m3 = ps['models']['M2'], ps['models']['M3']
    c, s, beta = m3['centers']['mark'], m3['scales']['mark'], m3['coefficients']['beta']
    x = {}
    for r in S.timing:
        f = led[r['emission_index']]
        x[r['emission_index']] = (math.log(current_durations(f, endpoint_nodes(f, ps['endpoint_mode'], int(ps['nodes'])))[0]) - c) / s
    xbar = sum(x.values()) / len(x)
    base2 = S.scores('M2', {})
    base3 = S.scores('M3', {})
    max_err = max(max(abs(base2[r['emission_index']] - r['M2']), abs(base3[r['emission_index']] - r['M3'])) for r in S.timing)
    best = minimize_scalar(lambda d: S.nll('M2', {'intercept': m2['intercept'] + d}), bounds=(-.5, .5), method='bounded',
                           options={'xatol': 1e-8}).x

    def gain_of(a3, a2):
        g = {r['emission_index']: 0.0 for r in prim_rows}
        for k in a3:
            g[k] = a3[k] - a2[k]
        return era_stat(prim_rows, g)

    m2_mark_level = S.scores('M2', {'intercept': m2['intercept'] + beta * xbar})
    m3_recentred = S.scores('M3', {'centers': {**m3['centers'], 'mark': c + xbar * s}})
    m2_best = S.scores('M2', {'intercept': m2['intercept'] + best})
    m3_best = S.scores('M3', {'intercept': m3['intercept'] + best})
    level = {
        'evaluation_mean_standardized_log_duration': xbar,
        'level_shift_implied_by_frozen_mark': beta * xbar,
        'frozen_M2_best_evaluation_level_shift': best,
        'max_score_recompute_error': max_err,
        'gain_frozen_M3_minus_M2': gain_of(base3, base2),
        'level_part_M2_shifted_by_mark_level_minus_M2': gain_of(m2_mark_level, base2),
        'slope_part_M3_recentred_minus_M2': gain_of(m3_recentred, base2),
        'slope_part_M3_minus_M2_shifted_by_mark_level': gain_of(base3, m2_mark_level),
        'M2_best_level_minus_M2': gain_of(m2_best, base2),
        'M3_minus_M2_both_at_best_M2_level': gain_of(m3_best, m2_best)}

    # 3. Type versus within-type, frozen M2 nuisance, free common level; by era.
    ts = params['type_within']
    T = Scorer(ts, led, ev, type_rows)
    m3t = ts['models']['M3']
    durs = {r['emission_index']: current_durations(led[r['emission_index']], endpoint_nodes(led[r['emission_index']], 'point', 1))[0]
            for r in T.timing}
    t_off = [m3t['coefficients']['beta_type'] * (d >= TYPE_SPLIT_D) + m3t['coefficients']['beta_within']
             * (math.log(d) - m3t['centers']['mark_type'][str(int(d >= TYPE_SPLIT_D))]) / m3t['scales']['mark_within'] for d in durs.values()]
    t_m3_best = T.scores('M3', {'intercept': m3t['intercept'] + best})
    t_m2_best = T.scores('M2', {'intercept': ts['models']['M2']['intercept'] + best})
    refits = type_refits(params, led, ev, prim_rows, type_rows, ERAS)
    gt = {r['emission_index']: 0.0 for r in type_rows}
    for k in t_m3_best:
        gt[k] = t_m3_best[k] - t_m2_best[k]
    typ = {
        'type_split_days': TYPE_SPLIT_D,
        'frozen_type_rule_uncentred_indicator_note': 'beta_type multiplies a 0/1 long indicator while the M2 intercept is fixed, so the frozen rule can lengthen post-long gaps but cannot shorten post-short gaps',
        'frozen_type_rule_mean_offset_on_evaluation': sum(t_off) / len(t_off),
        'frozen_type_rule_gain_both_at_best_M2_level': era_stat(type_rows, gt),
        'refits_frozen_M2_nuisance_free_level': refits}

    # Alternation.
    def lag(ledger):
        pairs = [(f['duration'], f['previous_duration']) for f in ledger
                 if f.get('duration') and f.get('previous_duration') and f['duration'] > 0 and f['previous_duration'] > 0]
        u = [math.log(d) for d, _ in pairs]
        v = [math.log(pd) for _, pd in pairs]
        mu, mv = sum(u) / len(u), sum(v) / len(v)
        r = sum((i - mu) * (j - mv) for i, j in zip(u, v)) / math.sqrt(sum((i - mu) ** 2 for i in u) * sum((j - mv) ** 2 for j in v))
        tr = Counter((int(pd >= TYPE_SPLIT_D), int(d >= TYPE_SPLIT_D)) for d, pd in pairs)
        return {'pairs': len(pairs), 'corr_log_duration_lag1': r,
                'share_long': sum(d >= TYPE_SPLIT_D for d, _ in pairs) / len(pairs),
                'p_long_after_long': tr[(1, 1)] / (tr[(1, 1)] + tr[(1, 0)]),
                'p_long_after_short': tr[(0, 1)] / (tr[(0, 1)] + tr[(0, 0)])}
    dev_dir = Path(a.dev_ledger).parent
    dev_params = json.loads((dev_dir / 'frozen_parameters.json').read_text())
    dev_led = {r['emission_index']: r for r in json.loads((dev_dir / 'ledger-0.0.json').read_text())}
    dev_ev = {r['emission_index']: r for r in json.loads((dev_dir / 'evidence-0.0.json').read_text())}
    typ['development_refits_in_sample'] = type_refits(
        dev_params, dev_led, dev_ev, json.loads((dev_dir / 'primary-scores.json').read_text()),
        json.loads((dev_dir / 'type_within-scores.json').read_text()), {'1910-1959': (-math.inf, START)})
    alternation = {'evaluation_1960_2017': lag(list(led.values())),
                   'development_1910_1959': lag(json.loads(Path(a.dev_ledger).read_text()))}

    out = {'scope': 'EXPLORATORY post-result review of the sealed SS Cyg 1960-2017 comparison; aggregates only; '
                    'cannot become a second confirmation; no 2018+ data',
           'input_sha256': {k: sha(v) for k, v in inputs.items()},
           'interval_recomputation': recompute, 'level_decomposition': level,
           'type_information': typ, 'alternation': alternation}
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    Path(a.output).write_text(json.dumps(out, indent=1, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
