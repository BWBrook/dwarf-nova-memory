#!/usr/bin/env python3
"""Record the authorized single pre-1960 fit, then profile frozen parameters."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from a10d_pipeline import source_state
from dnmem.directional_forecast import DirectionalBundle
from dnmem.oc_experiment import VARIANTS
from dnmem.real_development import require_gate, load_native, collect_ledgers, fit_variant, digest

EXTRA = ('scripts/a10e_real_fit.py', 'src/dnmem/real_development.py', 'src/dnmem/fit_profiles.py',
         'configs/a10e_real_fit.json', 'docs/protocols/a10e-real-development-fit-v1.md',
         'src/dnmem/aavso.py', 'src/dnmem/coverage.py')


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def frozen_source(freeze):
    state = source_state(freeze, False)
    for name in EXTRA:
        blob = subprocess.check_output(['git', 'show', f'{freeze}:{name}'], cwd=ROOT)
        actual = digest(ROOT/name)
        if hashlib.sha256(blob).hexdigest() != actual:
            raise ValueError('real-fit adapter differs from source freeze')
        state['source_sha256'][name] = actual
    return state


def fit(args):
    state = frozen_source(args.freeze_commit)
    config = json.loads((ROOT/'configs/a10e_real_fit.json').read_text())
    gate = require_gate(args.oc_directory, config)
    for name, expected in gate['source']['source_sha256'].items():
        if digest(ROOT/name) != expected:
            raise ValueError('a qualified forecasting/feature/extraction source changed')
    anchor = json.loads((ROOT/'configs/a04i_inputs.json').read_text())
    if digest(args.inputs) != anchor['prepared_inputs_sha256']:
        raise ValueError('not the approved anonymous source-identity cache')
    cache = json.loads(args.inputs.read_text())
    args.output.mkdir(parents=True, exist_ok=False)
    receipt = {'status': 'opening_authorized_native_sources', 'source': state,
               'gate_choice': config['gate_choice'], 'scope': config['scope'],
               'opened_utc': datetime.now(timezone.utc).isoformat(),
               'synthetic_receipt_sha256': digest(args.oc_directory/'receipt.json'),
               'input_cache_sha256': digest(args.inputs)}
    write(args.output/'receipt.json', receipt)
    rows, native = load_native(args.raw_root, cache, config)
    ledgers, evidence, concordance = collect_ledgers(rows, config)
    for delay in (0., 2.):
        write(args.output/f'ledger-{delay}.json', ledgers[delay])
        write(args.output/f'evidence-{delay}.json', evidence[delay])
    receipt.update(status='fitting', native=native, concordance=concordance,
                   first_real_fit_utc=datetime.now(timezone.utc).isoformat())
    write(args.output/'receipt.json', receipt)
    parameters, summaries = {}, {}
    for specification in VARIANTS:
        name, _, _, _, delay, _ = specification
        bundle, scores, summary = fit_variant(ledgers[delay], evidence[delay], config['stop_jd'], specification)
        parameters[name], summaries[name] = bundle.to_dict(), summary
        write(args.output/(name+'-model.json'), parameters[name])
        write(args.output/(name+'-scores.json'), scores)
        write(args.output/'frozen_parameters.json', parameters)
        write(args.output/'summary.json', summaries)
        print(name, 'frozen', flush=True)
    if frozen_source(args.freeze_commit) != state or digest(args.inputs) != receipt['input_cache_sha256']:
        raise ValueError('source or identity cache changed during fit')
    if native['source_sha256'] != {p.parent.name:digest(p) for p in sorted(args.raw_root.glob('aavso_ss_cyg_*/native.xml'))}:
        raise ValueError('native sources changed during fit')
    receipt.update(status='fit_completed', parameters_sha256=digest(args.output/'frozen_parameters.json'),
                   finished_utc=datetime.now(timezone.utc).isoformat())
    receipt['files_sha256'] = {p.name:digest(p) for p in sorted(args.output.iterdir()) if p.name != 'receipt.json'}
    write(args.output/'receipt.json', receipt)


def profiles(args):
    from dnmem.fit_profiles import profile_bundle
    initial = frozen_source(args.freeze_commit)
    receipt = json.loads((args.output/'receipt.json').read_text())
    if receipt['status'] != 'fit_completed' or receipt['source'] != initial:
        raise ValueError('profiling requires completed models at the exact source freeze')
    for name, expected in receipt['files_sha256'].items():
        if digest(args.output/name) != expected:
            raise ValueError('frozen real-fit payload changed')
    output = args.output/'profiles'
    output.mkdir(exist_ok=False)
    results = {}
    for name, _, _, _, delay, _ in VARIANTS:
        bundle = DirectionalBundle.from_dict(json.loads((args.output/(name+'-model.json')).read_text()))
        ledger = json.loads((args.output/f'ledger-{delay}.json').read_text())
        evidence = json.loads((args.output/f'evidence-{delay}.json').read_text())
        result = profile_bundle(bundle, ledger, evidence)
        results[name] = result
        write(output/(name+'.json'), result)
        print(name, 'profiled', flush=True)
    if frozen_source(args.freeze_commit) != initial or digest(args.output/'frozen_parameters.json') != receipt['parameters_sha256']:
        raise ValueError('profile diagnostics changed source or frozen parameters')
    write(output/'all.json', results)
    write(output/'receipt.json', {'status':'completed', 'source':initial,
                                  'parameters_sha256':receipt['parameters_sha256'],
                                  'files_sha256':{p.name:digest(p) for p in sorted(output.iterdir()) if p.name!='receipt.json'}})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('fit', 'profiles'))
    parser.add_argument('--freeze-commit', required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--oc-directory', type=Path, default=ROOT/'outputs/a10d_run_8f5df44/a10d_oc')
    parser.add_argument('--inputs', type=Path, default=ROOT/'outputs/a04i_inputs_frozen_20261108/inputs.json')
    parser.add_argument('--raw-root', type=Path, default=ROOT/'data/raw')
    args = parser.parse_args()
    (fit if args.stage=='fit' else profiles)(args)
