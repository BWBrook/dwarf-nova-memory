#!/usr/bin/env python3
"""Synthetic witness for how an onset bracket crossing a censor cutoff is routed."""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True
import argparse
from pathlib import Path
from unittest.mock import patch

from _review_support import (COMMIT, environment, load_verified_module, require,
                             verify_repo, write_output)


def run_case(module, lo: float, hi: float, stopping: str) -> dict:
    times = list(range(0, 41, 5))
    ledger = [{'emission_index': 0, 'emitted_at': 9.0, 'issue_time': 10.0}]
    if stopping == 'coverage':
        times.remove(25)
    else:
        ledger.append({'emission_index': 1, 'emitted_at': 19.0, 'issue_time': 20.0})
    rows = [{'JD': float(time)} for time in times]
    episode = {'confirmed_event': True, 'peak_t': 32.0,
               'onset_lo': lo, 'onset_hi': hi, 'onset_t': (lo + hi) / 2,
               'onset_method': 'synthetic_injected_bracket'}
    # Deliberately isolate the evidence builder. These are injected derived
    # episodes/visits, not photometry and not an assertion of an empirical case.
    with patch.object(module, 'visits', return_value=[{'t': float(time)} for time in times]), \
            patch.object(module, 'x4_episodes', return_value=[episode]):
        evidence = module.outcome_evidence(rows, ledger, stop=40.0)[0]
    return {key: evidence[key] for key in
            ('kind', 'reason', 'onset_lo', 'onset_hi', 'censor_at', 'survival_ambiguous')}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True, help='Local checkout with the exact pinned selected source bytes.')
    parser.add_argument('--output', type=Path, required=True, help='JSON output outside checkout; parent directory must exist.')
    args = parser.parse_args()
    repo = args.repo.expanduser().resolve(strict=True)
    paths = ('src/dnmem/__init__.py', 'src/dnmem/extract.py', 'src/dnmem/extract_x3.py',
             'src/dnmem/extract_x4.py', 'src/dnmem/prefix_features.py', 'src/dnmem/prefix_reference.py')
    checked = verify_repo(repo, paths)
    load_verified_module('dnmem', repo / paths[0], package=True)
    modules = {}
    for path in paths[1:]:
        name = 'dnmem.' + Path(path).stem
        modules[name] = load_verified_module(name, repo / path)
    implementations = (modules['dnmem.prefix_features'], modules['dnmem.prefix_reference'])
    results = []
    for stopping in ('coverage', 'superseded'):
        for name, lo, hi, expected in (
                ('before_cutoff', 16.0, 18.0, 'interval'),
                ('straddles_cutoff', 18.0, 22.0, 'right_censored'),
                ('after_cutoff', 22.0, 24.0, 'right_censored'),
                ('straddles_issue', 9.0, 11.0, 'excluded')):
            outputs = [run_case(module, lo, hi, stopping) for module in implementations]
            require(outputs[0] == outputs[1], f'Production/reference mismatch: {stopping}, {name}')
            result = outputs[0]
            require(result['kind'] == expected, f'Reviewed branch changed: {stopping}, {name}')
            if expected == 'right_censored':
                require(result['censor_at'] == 20.0 and result['reason'] == stopping,
                        f'Unexpected censoring time/reason: {stopping}, {name}')
            results.append({'scenario': name, 'stop_reason': stopping,
                            'input_bracket': [lo, hi], 'cutoff': 20.0,
                            'production_equals_reference': True, 'output': result})
    payload = {'scope': 'Synthetic injected evidence only; establishes a branch behavior, not its empirical frequency or score impact.',
               'reviewed_commit': COMMIT, 'environment': environment(), 'checked_repository_sources': checked,
               'implementations': [module.__name__ for module in implementations], 'calls': 16,
               'logical_witness': {'issue': 10.0, 'bracket': [18.0, 22.0], 'cutoff': 20.0,
                   'possible_onset': 19.0, 'inside_bracket': True, 'survives_cutoff': False},
               'results': results,
               'interpretation': 'Both implementations convert a bracket crossing the cutoff into right censoring at the cutoff. Membership in that bracket does not itself establish survival to the cutoff.',
               'limits': ['Extraction and visit summaries are mocked deliberately; this does not test whether real X4 observations generate the fixture.',
                          'No actual observation, empirical case count, or per-forecast score is read.',
                          'Agreement between implementations verifies concordance but does not validate the shared evidence contract.',
                          'This check does not quantify any effect on the reported primary comparison.']}
    write_output(args.output, payload, repo)


if __name__ == '__main__':
    main()
