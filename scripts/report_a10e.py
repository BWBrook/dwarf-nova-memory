#!/usr/bin/env python3
"""Compact public artifacts from the unchanged pre-1960 development fit."""

import argparse
import copy
import hashlib
import json
from pathlib import Path


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def report(directory, output):
    receipt=json.loads((directory/'receipt.json').read_text())
    profile_receipt=json.loads((directory/'profiles/receipt.json').read_text())
    params=directory/'frozen_parameters.json'
    if (receipt['status']!='fit_completed' or profile_receipt['status']!='completed'
            or sha(params)!=receipt['parameters_sha256']
            or sha(params)!=profile_receipt['parameters_sha256']):
        raise ValueError('frozen parameters/profiles do not reconcile')
    for folder, identity in ((directory, receipt), (directory/'profiles', profile_receipt)):
        for name,digest in identity['files_sha256'].items():
            if sha(folder/name)!=digest:raise ValueError('real-fit payload identity changed')
    profiles=copy.deepcopy(json.loads((directory/'profiles/all.json').read_text()))
    for variant in profiles.values():
        for model in variant['models'].values():
            for parameter in model['profiles'].values():
                parameter['evaluation_count']=len(parameter.pop('evaluations'))
    output.mkdir(parents=True,exist_ok=False)
    (output/'frozen_parameters.json').write_bytes(params.read_bytes())
    (output/'summary.json').write_bytes((directory/'summary.json').read_bytes())
    (output/'run-receipt.json').write_bytes((directory/'receipt.json').read_bytes())
    (output/'profiles.json').write_text(json.dumps(profiles,indent=2,sort_keys=True,allow_nan=False)+'\n')
    manifest={'source_freeze':receipt['source']['head'],'parameters_sha256':sha(params),
              'full_profiles_sha256':sha(directory/'profiles/all.json'),
              'profile_receipt_sha256':sha(directory/'profiles/receipt.json'),
              'interpretation':'in-sample development fit; conditional likelihood support is not calibrated confidence; no held-out skill result',
              'files_sha256':{p.name:sha(p) for p in sorted(output.iterdir())}}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report(args.directory,args.output)
