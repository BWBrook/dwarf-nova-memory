"""Guarded collection of the single, frozen pre-1960 development fit."""

from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics

from .coverage import combine_acquisitions
from . import prefix_features, prefix_reference
from .directional_forecast import fit_directional
from .oc_experiment import joint_valid


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require_gate(directory, config):
    directory = Path(directory)
    receipt_path = directory/'receipt.json'
    if digest(receipt_path) != config['simulation_receipt_sha256']:
        raise ValueError('not the accepted simulation receipt')
    receipt = json.loads(receipt_path.read_text())
    if (receipt['status'] != 'completed' or receipt['trials'] != 360
            or receipt['successful_trials'] != 360 or receipt['failed_trials'] != 0
            or receipt['source']['head'] != config['simulation_source']):
        raise ValueError('simulation grid did not complete at the accepted source')
    for name in ('summary.json', 'records.json'):
        if digest(directory/name) != receipt['files_sha256'][name]:
            raise ValueError('accepted simulation payload changed')
    summary = json.loads((directory/'summary.json').read_text())
    expected = {('v2-phase', case) for case in ('null', 'structured', 'gross', 'offset', 'adaptive')} | {('v4-phase', 'null')}
    checks = summary['null_rate_checks']
    calibration = [r for r in summary['calibration'] if r['cluster_years'] == 6]
    if (not summary['complete'] or not summary['screen_pass']
            or {(r['family'], r['case']) for r in checks} != expected or len(checks) != 6
            or any(r['successes']/r['trials'] > .05 or not r['screen_pass'] for r in checks)
            or len(calibration) != 2 or {r['case'] for r in calibration} != {'null', 'alternative'}
            or not all(r['pass'] for r in calibration)):
        raise ValueError('the accepted finite simulation screen did not pass')
    return receipt


def load_native(raw_root, cache, config):
    raw_root = Path(raw_root)
    if 'quarantine' in raw_root.absolute().parts or 'quarantine' in raw_root.resolve().parts:
        raise ValueError('reserved root rejected')
    paths = sorted(raw_root.glob('aavso_ss_cyg_*/native.xml'))
    expected = cache['source_sha256']
    if len(paths) != config['expected_acquisitions'] or len(expected) != config['expected_acquisitions']:
        raise ValueError('unexpected native acquisition inventory')
    if any('quarantine' in p.absolute().parts or 'quarantine' in p.resolve().parts for p in paths):
        raise ValueError('reserved acquisition path rejected')
    actual = {p.parent.name: digest(p) for p in paths}
    if actual != expected:
        raise ValueError('native acquisition identities changed')
    rows, duplicates = combine_acquisitions(paths)
    if any(not config['native_start_jd'] <= float(r['JD']) <= config['native_stop_jd'] for r in rows):
        raise ValueError('native row outside the accepted pre-1960 window')
    return rows, {'source_sha256': actual, 'native_rows': len(rows), 'duplicate_rows_removed': duplicates}


def collect_ledgers(rows, config):
    start, stop = config['start_jd'], config['stop_jd']
    if any(float(row['JD']) >= stop for row in rows):
        raise ValueError('evaluation-era row rejected before feature construction')
    ledgers, evidence, checks = {}, {}, {}
    for delay in (0., 2.):
        ledger = prefix_features.forecast_ledger(rows, latency=delay, start=start, stop=stop)
        reference = prefix_reference.forecast_ledger(rows, latency=delay, start=start, stop=stop)
        outcomes = prefix_features.outcome_evidence(rows, ledger, stop=stop)
        independent = prefix_reference.outcome_evidence(rows, reference, stop=stop)
        if ledger != reference or outcomes != independent:
            raise ValueError('real independent ledger/evidence mismatch')
        if any(f['prefix_last_jd'] > f['emitted_at'] or not start <= f['issue_time'] < stop for f in ledger):
            raise ValueError('real prefix information/window contract failed')
        ledgers[delay], evidence[delay] = ledger, outcomes
        payload = json.dumps([ledger, outcomes], sort_keys=True, allow_nan=False, separators=(',', ':')).encode()
        checks[str(delay)] = {'issued': len(ledger), 'candidate_reference_sha256': hashlib.sha256(payload).hexdigest()}
    return ledgers, evidence, checks


def fit_variant(ledger, outcomes, stop, specification):
    name, endpoint, local, mark, delay, joint = specification
    bundle = fit_directional(ledger, outcomes, stop, endpoint_mode=endpoint, local_level=local,
                             mark_mode=mark, joint_marks=joint)
    scores = [r for r in bundle.scores(ledger, outcomes) if r['M0'] is not None]
    if joint:
        ids = {f['emission_index'] for f in ledger if joint_valid(f)}
        scores = [r for r in scores if r['emission_index'] in ids]
    if not scores or any(not math.isfinite(r[m]) for r in scores for m in ('M0', 'M2', 'M3', 'P3')):
        raise ValueError('empty or nonfinite real development score')
    summary = {'issued': len(ledger), 'scored': len(scores),
               'evidence': dict(Counter(e['kind']+':'+e['reason'] for e in outcomes)),
               'routes': {m: dict(Counter(r[m+'_route'] for r in scores)) for m in ('M0', 'M2', 'M3', 'P3')},
               'log_likelihood': {m: sum(r[m] for r in scores) for m in ('M0', 'M2', 'M3', 'P3')},
               'mean_in_sample_gain': {'M3_M2': statistics.fmean(r['gain_M3_M2'] for r in scores),
                                      'P3_M2': statistics.fmean(r['gain_P3_M2'] for r in scores),
                                      'M3_P3': statistics.fmean(r['gain_M3_P3'] for r in scores),
                                      'M2_M0': statistics.fmean(r['M2']-r['M0'] for r in scores)},
               'interpretation': 'in-sample development likelihoods; not held-out skill'}
    return bundle, scores, summary
