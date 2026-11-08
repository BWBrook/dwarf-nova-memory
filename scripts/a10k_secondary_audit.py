"""Independent aggregate audit of C11--C13 and C24--C25 on opened saved data.

No candidate forecast, calibration, profile, or A10j analysis module is imported.
The point-end landmark likelihood and predictive quantiles are evaluated directly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import brentq, minimize, minimize_scalar
from scipy.special import betainc, log_ndtr, ndtri_exp


ROOT = Path(__file__).resolve().parents[1]
START, STOP = 2436934.5, 2458119.5
LR = 3.841


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def log_sf(value, mu, sigma):
    value = np.asarray(value, dtype=float)
    z = (np.log(np.maximum(value, np.finfo(float).tiny)) - mu) / sigma
    return np.where(value > 0, log_ndtr(-z), 0.0)


def log_difference(large, small):
    return large + np.log(-np.expm1(np.minimum(small - large, 0.0)))


def point_log_likelihood(mu, sigma, age, kind, lower, upper, censor):
    mu = np.broadcast_to(np.asarray(mu, dtype=float), age.shape)
    result = np.empty(len(age))
    mask = kind
    zlo = (np.log(lower[mask]) - mu[mask]) / sigma
    zhi = (np.log(upper[mask]) - mu[mask]) / sigma
    use_sf = zlo > 0
    probability = np.empty(len(zlo))
    probability[use_sf] = log_difference(log_ndtr(-zlo[use_sf]), log_ndtr(-zhi[use_sf]))
    probability[~use_sf] = log_difference(log_ndtr(zhi[~use_sf]), log_ndtr(zlo[~use_sf]))
    result[mask] = probability
    result[~mask] = log_sf(censor[~mask], mu[~mask], sigma)
    return result - log_sf(age, mu, sigma)


def design(features, model):
    q = np.log([f['previous_gap'] for f in features])
    levels = np.array([np.mean(f['earlier_gaps']) if f.get('earlier_gaps')
                       else model['centers']['earlier_level'] for f in features])
    return np.column_stack((np.ones(len(features)),
                            (q - model['centers']['previous_gap']) / model['scales']['previous_gap'],
                            (levels - model['centers']['earlier_level']) / model['scales']['earlier_level']))


def independent_association(ledger, evidence, secondary):
    association = secondary['association']
    saved = association['staged']['bundle']['models']
    m2 = saved['M2']
    outcomes = {x['emission_index']: x for x in evidence}
    f = [x for x in ledger if x.get('landmark_available') and x.get('previous_gap_covered') is True
         and x.get('previous_gap') is not None and x['previous_gap'] > 0
         and outcomes[x['emission_index']]['kind'] != 'excluded']
    assert len(f) == 436 and all(x['end_t'] is not None for x in f)
    end = np.array([x['end_t'] for x in f])
    issue = np.array([x['issue_time'] for x in f])
    o = [outcomes[x['emission_index']] for x in f]
    kinds = np.array([x['kind'] == 'interval' for x in o])
    lower = np.array([max(x['onset_lo'], x['issue_time']) - e if x['kind'] == 'interval' else 1.
                      for x, e in zip(o, end)])
    upper = np.array([x['onset_hi'] - e if x['kind'] == 'interval' else 2. for x, e in zip(o, end)])
    censor = np.array([x['censor_at'] - e if x['kind'] == 'right_censored' else 1.
                       for x, e in zip(o, end)])
    age = issue - end
    X = design(f, m2)
    base = np.array([m2['intercept'], m2['coefficients']['previous_gap'],
                     m2['coefficients']['earlier_level']])
    sigma = m2['sigma']
    mu = X @ base
    current = np.log([x['end_t'] - x['onset_t'] for x in f])
    previous = np.log([x['previous_duration'] for x in f])
    mark = {}
    for name, values, key in [('current', current, 'M3'), ('previous', previous, 'P3')]:
        assert abs(values.mean() - saved[key]['centers']['mark']) < 1e-12
        assert abs(values.std() - saved[key]['scales']['mark']) < 1e-12
        mark[name] = (values - values.mean()) / values.std()
    assert np.max(np.abs(X.mean(axis=0) - [1., 0., 0.])) < 1e-12
    assert np.max(np.abs(X[:, 1:].std(axis=0) - 1.)) < 1e-12

    def ll(v, sd=sigma):
        return point_log_likelihood(v, sd, age, kinds, lower, upper, censor)

    def baseline(theta):
        return -float(np.sum(ll(X @ theta[:3], math.exp(theta[3]))))

    frozen_theta = np.r_[base, math.log(sigma)]
    own_base = minimize(baseline, frozen_theta, method='Nelder-Mead',
                        options={'xatol': 1e-10, 'fatol': 1e-10, 'maxiter': 4000})
    assert own_base.success and np.all(np.isfinite(own_base.x))
    assert baseline(frozen_theta) - own_base.fun < 1e-5
    saved_base_nll = m2['metadata']['convergence']['objective']
    assert abs(baseline(frozen_theta) - saved_base_nll) < 1e-8

    separate = {}
    for name, column, model in [('current', mark['current'], 'M3'),
                                ('previous', mark['previous'], 'P3')]:
        objective = lambda beta: -float(np.sum(ll(mu + float(beta) * column)))
        fit = minimize_scalar(objective, bounds=(-5., 5.), method='bounded',
                              options={'xatol': 1e-12, 'maxiter': 1000})
        assert fit.success
        optimum = float(fit.fun)
        support = [brentq(lambda b: 2 * (objective(b) - optimum) - LR, -5., fit.x, xtol=1e-12),
                   brentq(lambda b: 2 * (objective(b) - optimum) - LR, fit.x, 5., xtol=1e-12)]
        original = association['staged']['profiles'][model]['profiles']['beta']
        original_support = original['likelihood_support_interval']
        assert abs(fit.x - original['estimate']) < 1e-6
        endpoint_error = max(abs(support[0] - original_support['lower']),
                             abs(support[1] - original_support['upper']))
        assert endpoint_error < 2e-6
        separate[name] = {'estimate': float(fit.x), 'support': support,
                          'saved_endpoint_max_abs_error': endpoint_error,
                          'nll_at_saved_estimate_difference': objective(original['estimate']) - optimum}

    Z = np.column_stack((mark['current'], mark['previous']))
    objective = lambda beta: -float(np.sum(ll(mu + Z @ np.asarray(beta))))
    fit = minimize(objective, np.zeros(2), method='Powell', bounds=[(-5., 5.)] * 2,
                   options={'xtol': 1e-11, 'ftol': 1e-13, 'maxiter': 2000})
    assert fit.success and np.all(np.isfinite(fit.x))
    profiles = {}
    for index, name in enumerate(('current_duration', 'previous_duration')):
        def profile(value):
            def nuisance(other):
                beta = fit.x.copy()
                beta[index], beta[1-index] = value, other
                return objective(beta)
            r = minimize_scalar(nuisance, bounds=(-5., 5.), method='bounded',
                                options={'xatol': 1e-12, 'maxiter': 1000})
            assert r.success
            return r.fun
        support = [brentq(lambda b: 2 * (profile(b) - fit.fun) - LR, -5., fit.x[index], xtol=1e-11),
                   brentq(lambda b: 2 * (profile(b) - fit.fun) - LR, fit.x[index], 5., xtol=1e-11)]
        original = association['joint']['profiles'][name]['likelihood_support_interval']
        error = max(abs(support[0] - original['lower']), abs(support[1] - original['upper']))
        assert error < 2e-6
        profiles[name] = {'estimate': float(fit.x[index]), 'support': support,
                          'saved_endpoint_max_abs_error': error}
    singular = np.linalg.svd(Z, compute_uv=False)
    kappa = float(singular[0] / singular[-1])
    correlation = float(np.corrcoef(Z.T)[0, 1])
    assert abs(kappa - association['joint']['identifiability']['condition_number']) < 1e-12
    return {'n': len(f), 'M2_nll_scalar_difference': baseline(frozen_theta) - saved_base_nll,
            'M2_independent_reoptimization_improvement': float(baseline(frozen_theta) - own_base.fun),
            'M2_reoptimized_parameter_max_abs_difference': float(np.max(np.abs(own_base.x-frozen_theta))),
            'separate': separate, 'joint': profiles, 'joint_nll_difference': float(fit.fun-association['joint']['objective']),
            'joint_design_correlation': correlation, 'joint_condition_number': kappa,
            'condition_number_from_correlation': math.sqrt((1+abs(correlation))/(1-abs(correlation)))}


def calibration(ledger, evidence, scores, parameters, secondary):
    assert parameters['endpoint_mode'] == 'point'
    by_id = {x['emission_index']: x for x in evidence}
    score_id = {x['emission_index']: x for x in scores}
    out = {}
    for label in ('M0', 'M2', 'M3'):
        result = {}
        for central in (.5, .9):
            counts = dict(covered=0, not_covered=0, undetermined=0)
            for f in ledger:
                e = by_id[f['emission_index']]
                if e['kind'] == 'excluded':
                    continue
                route = score_id[f['emission_index']][label + '_route']
                assert route in ('M0', 'M2', 'M3')
                model = parameters['models'][route]
                mu = float(model['intercept'])
                if route != 'M0':
                    q = (math.log(f['previous_gap'])-model['centers']['previous_gap'])/model['scales']['previous_gap']
                    level = np.mean(f['earlier_gaps']) if f.get('earlier_gaps') else model['centers']['earlier_level']
                    level = (level-model['centers']['earlier_level'])/model['scales']['earlier_level']
                    mu += model['coefficients']['previous_gap']*q+model['coefficients']['earlier_level']*level
                if route == 'M3':
                    x = (math.log(f['end_t']-f['onset_t'])-model['centers']['mark'])/model['scales']['mark']
                    mu += model['coefficients']['beta']*x
                sd = model['sigma']
                age = f['issue_time']-f['end_t']
                log_survival = float(log_sf(age, mu, sd))
                bounds = []
                for probability in ((1-central)/2, (1+central)/2):
                    log_tail = log_survival+math.log1p(-probability)
                    bounds.append(math.exp(mu-sd*float(ndtri_exp(log_tail)))-age)
                lo, hi = bounds
                if e['kind'] == 'interval':
                    a, b = e['onset_lo']-f['issue_time'], e['onset_hi']-f['issue_time']
                    classification = ('covered' if a >= lo and b <= hi else
                                      'not_covered' if b < lo or a > hi else 'undetermined')
                else:
                    classification = 'not_covered' if e['censor_at']-f['issue_time'] >= hi else 'undetermined'
                counts[classification] += 1
            n = sum(counts.values())
            reference = secondary['calibration']['models'][label]['central_intervals'][str(central)]
            assert all(counts[k] == reference[k] for k in counts)
            result[str(central)] = {**counts, 'n': n,
                                   'coverage_lower_bound': counts['covered']/n,
                                   'coverage_upper_bound': (counts['covered']+counts['undetermined'])/n}
        out[label] = result
    return out


def alternation(ledger):
    selected = [f for f in ledger if f.get('duration') and f.get('previous_duration')
                and f['duration'] > 0 and f['previous_duration'] > 0]
    duration = np.array([f['duration'] for f in selected])
    previous = np.array([f['previous_duration'] for f in selected])
    current_type, previous_type = duration >= 12., previous >= 12.
    matrix = [[int(np.sum((previous_type == i) & (current_type == j))) for j in (0, 1)] for i in (0, 1)]
    return {'pairs': len(selected), 'corr_log_duration_lag1': float(np.corrcoef(np.log(duration), np.log(previous))[0, 1]),
            'transitions_rows_previous_columns_current': matrix,
            'p_long_after_long': matrix[1][1]/sum(matrix[1]),
            'p_long_after_short': matrix[0][1]/sum(matrix[0]),
            'repeat_flag_count_in_pair_population': sum(bool(f.get('repeat_of_previous')) for f in selected)}


def block_statistics(rows):
    values = np.array([r['gain_M3_M2'] for r in rows])
    groups = np.floor((np.array([r['issue_time'] for r in rows])-START)/(6*365.25)).astype(int)
    keys = np.unique(groups)
    means = np.array([np.mean(values[groups == key]) for key in keys])
    residual_sums = np.array([np.sum(values[groups == key]-values.mean()) for key in keys])
    se = float(np.linalg.norm(residual_sums)/len(values)*math.sqrt(len(keys)/(len(keys)-1)))
    df = len(keys)-1
    critical = brentq(lambda x: 1.-.5*betainc(df/2, .5, df/(df+x*x))-.95, .01, 20.)
    leave = [float(values[groups != key].mean()) for key in keys]
    boundary = float(values.mean()/(critical*se))
    return {'n': len(values), 'blocks': len(keys), 'mean_gain': float(values.mean()), 'se': se,
            'critical_t_from_incomplete_beta': critical, 'blocks_positive': int(np.sum(means > 0)),
            'block_means': means.tolist(), 'leave_one_block_out_range': [min(leave), max(leave)],
            'share_positive_gains': float(np.mean(values > 0)), 'median_gain': float(np.median(values)),
            'SE_inflation_failure_boundary': boundary, 'lower_at_1_42_SE': float(values.mean()-critical*se*1.42),
            'lower_at_1_43_SE': float(values.mean()-critical*se*1.43),
            'strict_rule_note': 'The positive-bound rule passes only below the boundary, not at equality; 1.43 is a rounded boundary and does not itself pass.'}



def slow_state_counterexample():
    # Closed-form counterexample, not a fit to SS Cyg: two independent AR(1) components.
    rho_s, rho_a = .95, -.9
    a, b, c, d = .175, .350, .300, .001
    var_x, var_y = a*a+b*b, c*c+d*d
    cov_xy = a*c+b*d
    cov_yx_lag = a*c*rho_s+b*d*rho_a
    baseline = (c*c*rho_s+d*d*rho_a)/var_y
    partial_lag_covariance = cov_yx_lag-baseline*cov_xy
    partial_current_covariance = cov_xy-baseline*cov_yx_lag
    return {
        'scope': 'Analytic non-entailment example only; not fitted to data, not a competing empirical result.',
        'definition': 'log duration X=a*S+b*A; log gap Y=c*S+d*A; independent unit-variance stationary AR(1) components S,A; baseline conditions on previous Y.',
        'parameters': dict(rho_s=rho_s, rho_a=rho_a, a=a, b=b, c=c, d=d),
        'duration_lag_correlation': (a*a*rho_s+b*b*rho_a)/var_x,
        'slow_state_share_of_gap_variance': c*c/var_y,
        'slow_state_share_of_current_duration_gap_covariance': a*c/cov_xy,
        'lag_duration_gap_partial_covariance_given_previous_gap': partial_lag_covariance,
        'current_duration_gap_partial_covariance_given_previous_gap': partial_current_covariance,
        'slow_state_share_of_current_partial_covariance': (a*c-baseline*a*c*rho_s)/partial_current_covariance,
        'interpretation': 'Negative duration alternation and a negative separate lag association can coexist with dominant slow-state gap variation and current association; signs alone do not allocate mechanism.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'outputs/a10k_secondary_audit/summary.json')
    args = parser.parse_args()
    run = ROOT/'outputs/a10h_live_repair_5e39aeb'
    paths = {k: run/k for k in ('ledger-0.0.json', 'evidence-0.0.json', 'primary-scores.json',
                               'frozen_parameters.json', 'secondary.json')}
    paths['development_ledger'] = ROOT/'outputs/a10e_development_b80c4a9/ledger-0.0.json'
    paths['A10j_summary'] = ROOT/'data/provenance/a10j_postresult_review/summary.json'
    ledger, evidence, scores = (read(paths[k]) for k in ('ledger-0.0.json', 'evidence-0.0.json', 'primary-scores.json'))
    assert all(START <= x['issue_time'] < STOP for x in ledger)
    params, secondary, expected = read(paths['frozen_parameters.json']), read(paths['secondary.json']), read(paths['A10j_summary'])
    result = {'scope': 'Independent secondary/exploratory aggregate verification on already opened data only; no 2018+ access or candidate analysis imports',
              'input_sha256': {k: digest(p) for k, p in paths.items()}, 'script_sha256': digest(__file__),
              'C11_coverage': calibration(ledger, evidence, scores, params['primary'], secondary),
              'C12_C13_association': independent_association(ledger, evidence, secondary),
              'C24_alternation': {'evaluation': alternation(ledger), 'development': alternation(read(paths['development_ledger']))},
              'C25_block_statistics': block_statistics(scores),
              'analytic_slow_state_counterexample': slow_state_counterexample()}
    for own, name in [('evaluation', 'evaluation_1960_2017'), ('development', 'development_1910_1959')]:
        for key in ('corr_log_duration_lag1', 'p_long_after_long', 'p_long_after_short'):
            assert abs(result['C24_alternation'][own][key]-expected['alternation'][name][key]) < 1e-12
    ex = expected['interval_recomputation']
    assert result['C25_block_statistics']['blocks_positive'] == ex['blocks_positive']
    assert max(abs(x-y) for x,y in zip(result['C25_block_statistics']['leave_one_block_out_range'],ex['leave_one_block_out_range'])) < 1e-12
    assert abs(result['C25_block_statistics']['SE_inflation_failure_boundary']-ex['se_inflation_tolerated_before_rule_fails']) < 1e-12
    result['interpretation'] = {
        'C11': 'Support the numeric bracket-based observed-coverage bounds, conditional on the extracted onset brackets; they are partial identification in this realized sample, not confidence intervals, guaranteed physical-onset coverage or a formal calibration test.',
        'C12': 'Support the numeric conditional profiles. Replace follows from alternation with is compatible with alternation plus a current-mark association; the conditional coefficient is not causally decomposed.',
        'C13': 'Support the numeric joint profiles and modest full-rank condition number. The 436-row joint design has correlation -0.524814, distinct from the 441-pair C24 population. Correlation does not uniquely explain the zero-crossing intervals or establish nonidentifiability.',
        'C24': 'Support descriptive duration-pair alternation at forecast issuances, including one repeat-flagged record; this is not an independent unique-outburst catalog. A negative marginal correlation and lag coefficient do not exclude a slow positive latent component coexisting with a stronger alternating component.',
        'C25': 'Support the numbers with a rounding correction: failure threshold about 1.427 times SE; a 42% increase passes, an exact 43% increase fails. Influence and rescaling do not validate dependence assumptions.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
    print(json.dumps({'status': 'passed', 'output': str(args.output.resolve().relative_to(ROOT)),
                      'claims': ['C11', 'C12', 'C13', 'C24', 'C25'],
                      'SE_inflation_boundary': result['C25_block_statistics']['SE_inflation_failure_boundary']}))


if __name__ == '__main__':
    main()
