"""Acquire and qualify only the approved ten stars' pre-1990 development records."""

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from dnmem.g3a_acquisition import (END, STOP, TARGETS, ScopeViolation, UncertainCap, combine_rows,
                                   identity, parse_page, request_url, request_windows)

CONFIG = ROOT/'configs/g3a_feasibility.json'
SOURCES = ['scripts/g3a_execute.py', 'src/dnmem/g3a_acquisition.py',
           'src/dnmem/g3a_qualification.py', 'src/dnmem/g3a_eclipse.py',
           'configs/g3a_feasibility.json', 'docs/protocols/g3a-early-record-feasibility-v1.md',
           'data/access/g3a_authority.json',
           'src/dnmem/extract.py', 'src/dnmem/extract_x3.py', 'src/dnmem/extract_x4.py',
           'src/dnmem/extract_x5.py', 'src/dnmem/prefix_features.py',
           'src/dnmem/r2_features.py', 'src/dnmem/r2b_features.py',
           'src/dnmem/r2_scores.py', 'src/dnmem/r2_models.py', 'src/dnmem/r2b_models.py',
           'src/dnmem/r2b_scoring.py', 'uv.lock']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ScopeViolation('redirect refused before following potentially unbounded request')


def fetch(url, directory, label):
    opener = build_opener(NoRedirect())
    for attempt in range(1, 4):
        record = {'source_url': url, 'requested_at_utc': datetime.now(timezone.utc).isoformat(), 'attempt': attempt}
        stem = directory/f'{label}-attempt{attempt}'
        try:
            request = Request(url, headers={'User-Agent': 'dwarf-nova-memory/0.2 date-bounded development feasibility'})
            with opener.open(request, timeout=40) as response:
                payload = response.read(50_000_001)
                if len(payload)>50_000_000 or response.url!=url:
                    raise ValueError('oversized or redirected native response')
            native = stem.with_suffix('.xml')
            with native.open('xb') as stream:
                stream.write(payload)
            record.update(status='retained', bytes=len(payload), sha256=sha(native), native_file=native.name)
            write(stem.with_suffix('.json'), record)
            time.sleep(.2)
            return payload, record
        except (OSError, HTTPError) as exc:
            record.update(status='transport_failed', error_type=type(exc).__name__, http_status=getattr(exc,'code',None))
            write(stem.with_suffix('.json'), record)
            if attempt==3:
                raise
            time.sleep(attempt)


def acquire_star(star, directory, used_auids=None):
    directory.mkdir()
    name=star['name']
    payload, resolver=fetch(request_url(name, 1., END, metadata=True), directory, 'identity')
    root, auid=identity(payload,name)
    if used_auids is not None:
        if auid in used_auids:
            raise ScopeViolation('resolved AUID duplicates an earlier target')
        used_auids.add(auid)
    if root.find('Data') is not None and (root.findtext('Data') or '').strip():
        raise ScopeViolation('identity response unexpectedly contains observations')
    receipts=[resolver]
    groups=[]
    serial=0

    def window(start,end,depth=0):
        nonlocal serial
        serial+=1
        own=[]
        seen=set()
        for page in range(1,101):
            payload, receipt=fetch(request_url(name,start,end,auid=auid,page=page),directory,f'w{serial:04d}-p{page:03d}')
            receipt.update(start_jd=start,end_jd=end,page=page)
            receipts.append(receipt)
            try:
                rows,meta=parse_page(payload,name,auid,start,end,page)
            except UncertainCap:
                if depth>=20 or end-start<.01:
                    raise ValueError('cannot establish native window completeness')
                middle=(start+end)/2
                window(start,middle,depth+1);window(middle,end,depth+1)
                return
            receipt.update(meta, validated_rows=len(rows))
            new={r['obsID'] for r in rows}-seen
            if rows and not new:
                raise ValueError('pagination repeated a page without progress')
            seen.update(new)
            own.append(rows)
            if not meta['continue']:
                groups.extend(own)
                return
        raise ValueError('native pagination exceeded declared 100-page cap')

    for start,end in request_windows():
        window(start,end)
    rows,duplicates=combine_rows(groups)
    selected=[r for r in rows if r['band']=='Vis.' and r['val']=='V']
    write(directory/'acquisition.json',{'name':name,'auid':auid,'status':'completed',
          'stop_jd_exclusive':STOP,'requests':receipts,'native_unique_rows':len(rows),
          'duplicate_endpoint_rows':duplicates,'validated_visual_rows':len(selected)})
    return selected,{'name':name,'auid':auid,'native_unique_rows':len(rows),
                     'validated_visual_rows':len(selected),'duplicate_endpoint_rows':duplicates,
                     'native_files':[{'file':r['native_file'],'sha256':r['sha256'],'source_url':r['source_url']}
                                     for r in receipts]}


def qualification(star, rows):
    from dnmem.g3a_qualification import qualify_star
    if star['eclipsing_hold']:
        from dnmem.g3a_eclipse import qualify_eclipse_star
        return qualify_eclipse_star(rows, star, STOP)
    return qualify_star(rows,star['name'],threshold=star['threshold'],stop=STOP)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze-commit',required=True)
    parser.add_argument('--raw',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    for path in (args.raw,args.output):
        if path.exists() or 'quarantine' in path.resolve().parts:
            parser.error('require fresh non-quarantine output paths')
        relative=path.resolve().relative_to(ROOT)
        if subprocess.run(['git','check-ignore','-q',str(relative/'payload.json')],cwd=ROOT).returncode:
            parser.error('native and individual artifacts must be ignored')
    freeze=subprocess.check_output(['git','rev-parse',args.freeze_commit],cwd=ROOT,text=True).strip()
    for path in SOURCES:
        if subprocess.check_output(['git','show',freeze+':'+path],cwd=ROOT)!=(ROOT/path).read_bytes():
            raise ValueError('source differs from acquisition freeze: '+path)
    config=json.loads(CONFIG.read_text())
    if tuple(s['name'] for s in config['stars'])!=TARGETS or config['stop_jd_exclusive']!=STOP:
        raise ValueError('approved target/split registry changed')
    authority=json.loads((ROOT/'data/access/g3a_authority.json').read_text())
    if (authority['status']!='approved_for_frozen_execution' or tuple(authority['targets'])!=TARGETS
            or authority['stop_jd_exclusive']!=STOP):
        raise ValueError('G3a authority does not match this execution')
    args.raw.mkdir(parents=True);args.output.mkdir(parents=True)
    receipt={'status':'running','freeze_commit':freeze,'start_utc':datetime.now(timezone.utc).isoformat(),
             'source_sha256':{p:sha(ROOT/p) for p in SOURCES},'python':sys.version,'platform':platform.platform(),
             'numpy':importlib.metadata.version('numpy'),'scipy':importlib.metadata.version('scipy'),
             'authority':'Barry chat10November2026: yes, approved as proposed. Continue.',
             'stop_jd_exclusive':STOP}
    write(args.output/'receipt.json',receipt)
    result=[]
    used_auids=set()
    for star in config['stars']:
        print(json.dumps({'star':star['name'],'stage':'date_bounded_acquisition'}),flush=True)
        try:
            rows,metadata=acquire_star(star,args.raw/star['slug'],used_auids=used_auids)
            print(json.dumps({'star':star['name'],'stage':'gain_free_qualification','validated_visual_rows':len(rows)}),flush=True)
            qualified=qualification(star,rows)
            private=qualified.pop('_private',{})
            write(args.output/(star['slug']+'-individual-unreleased.json'),private)
            result.append({'name':star['name'],'status':'completed','acquisition':metadata,**qualified})
        except ScopeViolation as exc:
            result.append({'name':star['name'],'status':'access_guard_stopped','qualified':False,
                           'error_type':type(exc).__name__,'error':str(exc)})
            write(args.output/'summary.json',{'stars':result,'stop_jd_exclusive':STOP,'scope':'access guard stopped all later requests'})
            receipt.update(status='access_guard_stopped',error=str(exc),end_utc=datetime.now(timezone.utc).isoformat())
            write(args.output/'receipt.json',receipt)
            raise
        except Exception as exc:
            result.append({'name':star['name'],'status':'failed','qualified':False,'error_type':type(exc).__name__,
                           'error':str(exc)[:300]})
        write(args.output/'summary.json',{'stars':result,'stop_jd_exclusive':STOP,'scope':'gain-free development feasibility'})
        print(json.dumps({'star':star['name'],'status':result[-1]['status'],'qualified':result[-1]['qualified']}),flush=True)
    cohort=[r['name'] for r in result if r.get('qualified')]
    write(args.output/'qualified-set.json',{'names':cohort,'frozen_before_mark_fit':True,
          'development_stop_exclusive':STOP,'no_mark_fit_performed':True})
    receipt.update(status='completed',end_utc=datetime.now(timezone.utc).isoformat(),qualified=len(cohort),
                   failed_targets=sum(r['status']=='failed' for r in result),
                   output_sha256={p.name:sha(p) for p in args.output.iterdir() if p.name!='receipt.json'})
    write(args.output/'receipt.json',receipt)


if __name__=='__main__':
    main()
