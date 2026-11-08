#!/usr/bin/env python3
"""Emit compact A10d tables from a completed, independently checked run."""

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import statistics


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report(directory, output):
    receipt = json.loads((directory/'receipt.json').read_text())
    records = json.loads((directory/'records.json').read_text())
    summary = json.loads((directory/'summary.json').read_text())
    if receipt['status'] != 'completed' or receipt['trials'] != 360 or not summary['complete']:
        raise ValueError('the fixed grid must complete without missing or failed trials')
    for filename in ('records.json', 'summary.json'):
        if digest(directory/filename) != receipt['files_sha256'][filename]:
            raise ValueError('completed payload identity changed')
    cases = []
    keys = sorted({tuple(row['task'][:2]) for row in records})
    for family, case in keys:
        group = [r['result'] for r in records if r['task'][:2] == [family, case]]
        fits = [r['models']['primary']['models']['M3'] for r in group]
        betas = [r['coefficients']['beta'] for r in fits]
        secondary = [r['secondary_evaluation_fit']['models']['M3']['coefficients']['beta'] for r in group]
        primary = [r['intervals']['primary']['6']['gain_M3_M2'] for r in group]
        evidence = Counter()
        for row in group:
            evidence.update(row['counts']['evaluation_evidence'])
        cases.append({'family': family, 'case': case, 'trials': len(group),
                      'mean_evaluation_issued': statistics.fmean(r['counts']['evaluation_issued'] for r in group),
                      'evaluation_evidence_totals': dict(evidence),
                      'positive_gain_trials': sum(r['estimate'] > 0 for r in primary),
                      'interval_halfwidth': {'median': statistics.median((r['upper']-r['lower'])/2 for r in primary),
                                             'mean': statistics.fmean((r['upper']-r['lower'])/2 for r in primary)},
                      'beta': {'mean': statistics.fmean(betas), 'sd': statistics.stdev(betas),
                               'median': statistics.median(betas), 'min': min(betas), 'max': max(betas),
                               'exact_zero': sum(b == 0 for b in betas),
                               'at_bound_metadata': sum(r['metadata']['at_bound'] for r in fits)},
                      'secondary_evaluation_beta': {'mean': statistics.fmean(secondary),
                                                   'sd': statistics.stdev(secondary),
                                                   'negative': sum(b < 0 for b in secondary)},
                      'comparisons': [r for r in summary['rows'] if r['family'] == family and r['case'] == case
                                      and r['variant'] == 'primary' and r['cluster_years'] == 6]})
    output.mkdir(parents=True, exist_ok=False)
    public = {'source_freeze': receipt['source']['head'], 'input_sha256': receipt['input_sha256'],
              'seed_base': receipt['seed_base'], 'trials': receipt['trials'],
              'elapsed_seconds': receipt['elapsed_seconds'], 'environment': receipt['source']['environment'],
              'concordance_identity': receipt['concordance_identity'],
              'payload_receipt_sha256': digest(directory/'receipt.json'),
              'payload_records_sha256': digest(directory/'records.json'),
              'payload_summary_sha256': digest(directory/'summary.json'),
              'screen_pass': summary['screen_pass'], 'formal_certification_pass': summary['formal_certification_pass'],
              'null_rate_checks': summary['null_rate_checks'], 'calibration': summary['calibration'],
              'cases': cases, 'real_fit_automatic': False,
              'scope': 'synthetic operating-characteristic screen, not a real-star forecast result or size certificate'}
    (output/'report.json').write_text(json.dumps(public, indent=2, sort_keys=True, allow_nan=False)+'\n')
    fields = ('family', 'case', 'variant', 'cluster_years', 'comparison', 'mean_gain', 'trial_sd', 'mean_n',
              'successes', 'trials', 'rate', 'mc_se', 'exact_lower95', 'exact_upper95', 'one_sided_upper95')
    with (output/'comparisons.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fields, lineterminator='\n')
        writer.writeheader()
        for row in summary['rows']:
            writer.writerow({**{k: v for k, v in row.items() if k != 'rejections'}, **row['rejections']})
    (output/'run-receipt.json').write_bytes((directory/'receipt.json').read_bytes())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report(args.directory, args.output)
