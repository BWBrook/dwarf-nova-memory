"""Bounded receipt-first acquisition; transport is supplied explicitly."""

from datetime import date,datetime,timezone
import hashlib
import json
import math
from pathlib import Path

from .evaluation_native import EVALUATION_START_JD,EVALUATION_CUTOFF_JD,RowCapError,request_url,parse_native_bytes
from .evaluation import START,STOP,write

TERMS_URL='https://aavso.org/data-usage-guidelines-2026-07/'


def calendar_windows():
    windows=[(EVALUATION_START_JD,START)]
    for year in range(1960,2018):
        begin=START+(date(year,1,1)-date(1960,1,1)).days
        end=START+(date(year+1,1,1)-date(1960,1,1)).days
        windows.append((begin,math.nextafter(end,-math.inf) if end==STOP else end))
    return windows


def acquire(raw_root,transport,*,mode,receipt_callback=None):
    root=Path(raw_root);root.mkdir(parents=True,exist_ok=False)
    manifest=[]
    def window(start,end,depth=0):
        if depth>40 or not start<end or end-start>366 or end>=EVALUATION_CUTOFF_JD:
            raise ValueError('invalid or unsplittable request window')
        url=request_url(start,end)
        payload,extra=transport(start,end,url)
        if not isinstance(payload,bytes):raise ValueError('transport must return raw response bytes')
        namespace=hashlib.sha256(root.name.encode()).hexdigest()[:10]
        identity=f'aavso_ss_cyg_evaluation_{namespace}_{len(manifest):04d}'
        folder=root/identity;folder.mkdir()
        (folder/'native.xml').write_bytes(payload)
        receipt={**extra,'source_url':url,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),
                 'sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload),
                 'mode':mode,'terms_url':TERMS_URL,'status':'retained_before_parsing'}
        write(folder/'receipt.json',receipt)
        row={'provenance_id':identity,'source_url':url,'retrieved_at_utc':receipt['retrieved_at_utc'],
             'sha256':receipt['sha256'],'bytes':len(payload),'raw_relative_path':str(Path('raw')/identity/'native.xml'),
             'native_time_format':'JD','native_time_scale':'unresolved','native_time_reference':'unresolved',
             'licence_or_terms_url':TERMS_URL,'redistribution_status':'raw bytes excluded from Git','status':'retained_before_parsing'}
        manifest.append(row)
        write(root/'acquisitions.json',manifest)
        if receipt_callback:receipt_callback(row)
        try:
            _,metadata=parse_native_bytes(payload,start_jd=start,end_jd=end)
        except RowCapError:
            receipt['status']=row['status']='split_parent_row_cap'
            write(folder/'receipt.json',receipt);write(root/'acquisitions.json',manifest)
            middle=(start+end)/2
            if not start<middle<end:raise ValueError('row-cap window cannot be split further')
            return window(start,middle,depth+1)+window(middle,end,depth+1)
        receipt.update(status='validated',metadata=metadata)
        row['status']='validated'
        write(folder/'receipt.json',receipt);write(root/'acquisitions.json',manifest)
        return [folder/'native.xml']
    paths=[]
    for start,end in calendar_windows():paths.extend(window(start,end))
    return paths,manifest
