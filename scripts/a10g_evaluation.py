#!/usr/bin/env python3
"""Sealed evaluation and synthetic rehearsal; live access requires committed approval."""

import argparse
import csv
from datetime import datetime,timezone
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler,Request,build_opener

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from dnmem.evaluation import START,STOP,PARAMETER_SHA256,evaluate_frozen,secondary_diagnostics,write
from dnmem.evaluation_access import require_authorization
from dnmem.evaluation_acquire import acquire,TERMS_URL
from dnmem.evaluation_native import combine_native,select_analysis_rows
from dnmem.evaluation_rehearsal import surrogate
from dnmem.real_development import load_native

PROTOCOL='docs/protocols/a10g-sealed-evaluation-v1.md'
AUTHORITY='coordination/evaluation_access.json'
PARAMETERS='data/fits/a10e_1910_1959/frozen_parameters.json'
MANIFEST='data/manifests/acquisitions.csv'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*arguments):return subprocess.check_output(['git',*arguments],cwd=ROOT,text=True).strip()


def source_proof(freeze,*,live=False,allow_manifest=False):
    head=git('rev-parse','HEAD')
    if freeze!=git('rev-parse',freeze+'^{commit}'):
        raise ValueError('the full source-freeze commit hash is required')
    subprocess.run(['git','merge-base','--is-ancestor',freeze,head],cwd=ROOT,check=True,capture_output=True)
    dirty=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
    if any(not(allow_manifest and line[3:]==MANIFEST) for line in dirty.splitlines()):
        raise ValueError('sealed execution requires a clean checkout apart from its append-only acquisition manifest')
    proof_path='data/simulations/a10d_20261108/run-receipt.json'
    names=git('ls-tree','-r','--name-only',freeze,'--','src','scripts','configs','pyproject.toml','uv.lock').splitlines()+[PROTOCOL,PARAMETERS,proof_path]
    hashes={}
    for name in names:
        blob=subprocess.check_output(['git','show',f'{freeze}:{name}'],cwd=ROOT)
        expected=hashlib.sha256(blob).hexdigest()
        if sha(ROOT/name)!=expected:raise ValueError('source/parameter drift from freeze: '+name)
        hashes[name]=expected
    if sha(ROOT/proof_path)!='be0e25cd6d5432ca4cf3283991e698ca4b205c7424d16aff88e01abe02ae6f82':
        raise ValueError('original qualification receipt changed')
    retained=json.loads((ROOT/proof_path).read_text())
    for name,expected in retained['source']['source_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('qualified forecasting source changed: '+name)
    if sha(ROOT/PARAMETERS)!=PARAMETER_SHA256:raise ValueError('real training parameters changed')
    return {'freeze_commit':freeze,'execution_commit':head,'sha256':hashes,
            'parameters_sha256':PARAMETER_SHA256,'protocol_sha256':sha(ROOT/PROTOCOL)}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None


def live_transport(start,end,url):
    request=Request(url,headers={'User-Agent':'dwarf-nova-memory/0.1 sealed bounded evaluation'})
    try:
        response=build_opener(NoRedirect).open(request,timeout=60)
        with response:
            return response.read(),{'final_url':response.url,'http_status':response.status}
    except HTTPError as exc:
        return exc.read(),{'final_url':url,'http_status':exc.code,'http_error':str(exc)}


def extend_private_id_cache(context,all_rows):
    def identity(row):
        value=(str(row.get('obsName') or '').strip() or str(row['by']).strip()).casefold()
        if not value:raise ValueError('empty selected observer identity')
        return value
    old=sorted({identity(r) for r in context if r['band']=='Vis.' and r['val']=='V'})
    mapping={value:f'o{i:04d}' for i,value in enumerate(old,1)}
    new=sorted({identity(r) for r in all_rows if r['band']=='Vis.' and r['val']=='V'}-set(mapping))
    for value in new:mapping[value]=f'o{len(mapping)+1:04d}'
    return {'mapping':mapping,'scope':'private diagnostic identity map; never applied to frozen forecasting input; original cache is not modified'}


def append_public_receipt(row,raw_root):
    path=ROOT/MANIFEST
    existing=path.read_text();fields=next(csv.reader(io.StringIO(existing)))
    from urllib.parse import urlparse
    values={'provenance_id':row['provenance_id'],'target_id':'ss_cyg','provider':'AAVSO AID via official VStar/VSX service',
            'query_or_request':urlparse(row['source_url']).query,'source_url':row['source_url'],
            'retrieved_at_utc':row['retrieved_at_utc'],'available_until':'unknown: historical ingestion/revision times not available',
            'raw_relative_path':str((raw_root/Path(row['raw_relative_path']).relative_to('raw')).relative_to(ROOT)),
            'sha256':row['sha256'],'native_time_format':'JD','native_time_scale':'unresolved','native_time_reference':'unresolved',
            'passbands':'retained in private receipt; analysis is Vis./V only','licence_or_terms_url':TERMS_URL,
            'redistribution_status':'raw export not committed; redistribution permission not established',
            'software_version':'sealed A10g runner','notes':'receipt retained before parsing; automated result sealed before inspection'}
    with path.open('a',newline='') as handle:
        writer=csv.DictWriter(handle,fields,lineterminator='\n');writer.writerow(values)


def run(args):
    live=args.mode=='live'
    initial=source_proof(args.freeze_commit,live=live)
    authority=None
    if live:
        authority=require_authorization(ROOT/AUTHORITY,args.freeze_commit,ROOT/PROTOCOL)
        subprocess.run(['git','ls-files','--error-unmatch',AUTHORITY],cwd=ROOT,check=True,capture_output=True)
        published=git('ls-remote','origin','refs/heads/main').split()
        if not published or published[0]!=initial['execution_commit']:
            raise PermissionError('commit and push the exact access decision before requesting data')
    args.output.mkdir(parents=True,exist_ok=False)
    receipt={'mode':args.mode,'status':'running','source':initial,'parameters_sha256':PARAMETER_SHA256,
             'started_utc':datetime.now(timezone.utc).isoformat(),'stages':{},'concordance_pass':False}
    write(args.output/'receipt.json',receipt)
    manifest_before=(ROOT/MANIFEST).read_bytes()
    auth_hash=sha(ROOT/AUTHORITY) if live else None
    def stage(name):
        receipt['stages'][name]=datetime.now(timezone.utc).isoformat()
        if name=='concordance_passed':receipt['concordance_pass']=True
        write(args.output/'receipt.json',receipt)
    try:
        anchor=json.loads((ROOT/'configs/a04i_inputs.json').read_text())
        if sha(args.inputs)!=anchor['prepared_inputs_sha256']:raise ValueError('not the frozen pre1960 anonymous benchmark cache')
        inputs=json.loads(args.inputs.read_text())
        if live:
            config=json.loads((ROOT/'configs/a10e_real_fit.json').read_text())
            context,_=load_native(ROOT/'data/raw',inputs,config)
            raw_root=ROOT/'data/raw'/('a10g_evaluation_'+args.freeze_commit[:12])
            def transport(start,end,url):
                if sha(ROOT/AUTHORITY)!=auth_hash:raise PermissionError('approval changed during acquisition')
                return live_transport(start,end,url)
            rehearsal_metadata=None
        else:
            selected=json.loads((ROOT/'configs/a04i_selected.json').read_text())['v2-phase']
            context,transport,rehearsal_metadata=surrogate(inputs,selected,'a10f-rehearsal|'+args.freeze_commit)
            raw_root=args.output/'raw'
        stage('acquisition_started')
        paths,acquisitions=acquire(raw_root,transport,mode=args.mode,
                                 receipt_callback=(lambda row:append_public_receipt(row,raw_root)) if live else None)
        stage('acquisition_completed')
        later,acquisition_proof=combine_native(paths)
        if any(json.loads((p.parent/'receipt.json').read_text())['mode']!=args.mode for p in paths):
            raise ValueError('rehearsal/live acquisition modes cannot mix')
        seen={}
        for row in context+later:
            identity=row['obsID']
            if identity in seen and seen[identity]!=row:raise ValueError('conflicting overlap with pre1960 context')
            seen[identity]=row
        combined=sorted(seen.values(),key=lambda r:(float(r['JD']),r['obsID']))
        if any(float(r['JD'])>=STOP for r in combined):raise ValueError('reserved observation rejected')
        write(args.output/'observer_ids.json',extend_private_id_cache(context,combined))
        analysis=select_analysis_rows(combined)
        stage('native_verified')
        ledgers,evidence,concordance,variants,bundles=evaluate_frozen(analysis,ROOT/PARAMETERS,args.output,stage_callback=stage)
        write(args.output/'secondary.json',secondary_diagnostics(ledgers,evidence,variants,bundles))
        stage('secondary_completed')
        final=source_proof(args.freeze_commit,live=live,allow_manifest=live)
        if final!=initial:raise ValueError('source changed during sealed execution')
        if live and (not(ROOT/MANIFEST).read_bytes().startswith(manifest_before) or sha(ROOT/AUTHORITY)!=auth_hash):
            raise ValueError('authority or acquisition-manifest history changed')
        receipt.update(status='completed',finished_utc=datetime.now(timezone.utc).isoformat(),
                       concordance_sha256=sha(args.output/'concordance.json'),
                       acquisitions=acquisition_proof,rehearsal_metadata=rehearsal_metadata,
                       input_sha256=sha(args.inputs),observer_ids_sha256=sha(args.output/'observer_ids.json'))
        receipt['files_sha256']={p.name:sha(p) for p in sorted(args.output.iterdir()) if p.is_file() and p.name!='receipt.json'}
        write(args.output/'receipt.json',receipt)
    except Exception as exc:
        receipt.update(status='failed',error_type=type(exc).__name__,error=str(exc),failed_utc=datetime.now(timezone.utc).isoformat())
        write(args.output/'receipt.json',receipt)
        raise
    print(json.dumps({'status':receipt['status'],'mode':args.mode,'primary_result':str(args.output/'primary.json')}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=('rehearsal','live'),default='rehearsal')
    p.add_argument('--freeze-commit',required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--inputs',type=Path,default=ROOT/'outputs/a04i_inputs_frozen_20261108/inputs.json')
    run(p.parse_args())
