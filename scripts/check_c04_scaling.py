#!/usr/bin/env python3
"""Independently derive C04's fixed-history clock-scale contrast from frozen parameters."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('data/fits/a10e_1910_1959/frozen_parameters.json')
FROZEN_SHA256 = 'ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3'


def main():
    raw = (ROOT / SOURCE).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != FROZEN_SHA256:
        raise ValueError('frozen parameter bytes changed')
    models = json.loads(raw)['primary']['models']
    beta = models['M3']['coefficients']['beta']
    scale = models['M3']['scales']['mark']
    standardised_change = math.log(2) / scale
    shift = beta * standardised_change
    print(json.dumps({
        'claim': 'C04', 'source': str(SOURCE), 'source_sha256': digest,
        'n_fit': {name: models[name]['n_fit'] for name in ('M0', 'M2', 'M3')},
        'duration_beta': beta, 'log_duration_scale': scale,
        'duration_multiplier': 2, 'standardised_log_duration_change': standardised_change,
        'log_clock_median_change': shift,
        'untruncated_clock_median_ratio': math.exp(shift),
        'untruncated_clock_median_change_percent': 100 * math.expm1(shift),
        'scope': 'Fixed timing predictors; untruncated quiet-gap clock median exp(mu). '
                 'This ratio is not the survival-conditioned remaining-wait median ratio.'
    }, indent=2, sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
