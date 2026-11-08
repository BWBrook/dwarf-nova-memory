"""Synthetic native-format surrogate; never requests an archive observation."""

from bisect import bisect_left,bisect_right
import csv
import io
import math

from .evaluation import START,STOP
from .evaluation_native import AUID,EVALUATION_START_JD
from .oc_streams import development_stream


def native_payload(rows):
    columns=['obsID','JD','mag','uncert','fainterThan','band','by','val','obsName','commentCode','timeReference']
    stream=io.StringIO();writer=csv.DictWriter(stream,columns,lineterminator='\n');writer.writeheader()
    for row in rows:writer.writerow({name:row.get(name,'') for name in columns})
    return (f'<VSXObject><Name>SS Cyg</Name><AUID>{AUID}</AUID><Count>{len(rows)}</Count>'
            '<TimeReference>synthetic native JD; no conversion</TimeReference><Data><![CDATA['
            +stream.getvalue()+']]></Data></VSXObject>').encode()


def surrogate(inputs,configuration,base,case='alternative'):
    rows,truth,metadata=development_stream(inputs,configuration,case,0,base)
    shift=START-float(metadata['eval_start'])
    if abs(shift-round(shift))>1e-6:raise ValueError('surrogate must preserve native night bins')
    shift=int(round(shift))
    copied=[]
    for row in rows:
        jd=float(row['JD'])+shift
        if not START-400<=jd<STOP:continue
        copied.append({**row,'JD':str(jd),'obsID':'rehearsal-'+row['obsID'],
                       'commentCode':'SIM N','timeReference':'synthetic geocentric-like JD'})
    context=[r for r in copied if float(r['JD'])<=EVALUATION_START_JD]
    later=[r for r in copied if float(r['JD'])>=EVALUATION_START_JD]
    for index in range(150):
        jd=START+index*130.25
        later.extend([{'obsID':f'synthetic-ccd-{index}','JD':str(jd),'mag':'2.0','uncert':'.01',
                       'fainterThan':'0','band':'V','by':'SIMCCD','val':'V','obsName':'SIMCCD','commentCode':'CCD','timeReference':'JD'},
                      {'obsID':f'synthetic-rejected-{index}','JD':str(jd+.1),'mag':'2.0','uncert':'',
                       'fainterThan':'0','band':'Vis.','by':'SIMD','val':'D','obsName':'SIMD','commentCode':'bad','timeReference':'JD'}])
    boundary={'obsID':'synthetic-boundary','JD':str(EVALUATION_START_JD),'mag':'12.0','uncert':'',
              'fainterThan':'1','band':'Vis.','by':'BOUNDARY','val':'V','obsName':'BOUNDARY',
              'commentCode':'synthetic overlap','timeReference':'JD'}
    context.append(boundary);later.append(boundary)
    later.sort(key=lambda r:(float(r['JD']),r['obsID']))
    times=[float(r['JD']) for r in later]
    def transport(start,end,url):
        part=later[bisect_left(times,start):bisect_right(times,end)]
        return native_payload(part),{'synthetic':True,'final_url':url}
    return context,transport,{'seed_base':base,'case':case,'source_metadata':metadata,
                             'translation_days':shift,'scope':'synthetic fixture dates, not archived 1960+ observations'}
