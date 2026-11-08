"""Frozen-parameter held-out evaluation, with concordance before any score."""

from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path

from .directional_forecast import DirectionalBundle
from . import prefix_features, prefix_reference
from .oc_experiment import VARIANTS, COMPARISONS, joint_valid
from .oc_statistics import cluster_interval
from .forecast_calibration import calibration_summary, standardized_feature_summary

START=2436934.5
STOP=2458119.5
ERA_BOUNDARY=START+(date(1993,1,1)-date(1960,1,1)).days
PARAMETER_SHA256='ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3'
REFERENCE_GAIN=0.004519560867443926


def canonical(value):return json.dumps(value,sort_keys=True,allow_nan=False,separators=(',',':'))


def digest_value(value):return hashlib.sha256(canonical(value).encode()).hexdigest()


def write(path,value):Path(path).write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def ledger_concordance(rows,output):
    ledgers,evidence,checks={},{},{}
    for delay in (0.,2.):
        a=prefix_features.forecast_ledger(rows,latency=delay,start=START,stop=STOP)
        b=prefix_reference.forecast_ledger(rows,latency=delay,start=START,stop=STOP)
        ea=prefix_features.outcome_evidence(rows,a,stop=STOP)
        eb=prefix_reference.outcome_evidence(rows,b,stop=STOP)
        different=[]
        for label,left,right in (('ledger',a,b),('evidence',ea,eb)):
            li={v['emission_index']:v for v in left};ri={v['emission_index']:v for v in right}
            different.extend({'kind':label,'emission_index':i} for i in sorted(set(li)|set(ri)) if li.get(i)!=ri.get(i))
        checks[str(delay)]={'match':a==b and ea==eb,'differences':different,
                            'candidate_sha256':digest_value([a,ea]),'reference_sha256':digest_value([b,eb])}
        ledgers[delay],evidence[delay]=a,ea
        write(output/f'ledger-{delay}.json',a);write(output/f'evidence-{delay}.json',ea)
    write(output/'concordance.json',checks)
    if not all(v['match'] for v in checks.values()):
        raise ValueError('independent ledger/evidence mismatch; primary remains sealed')
    return ledgers,evidence,checks


def evaluate_frozen(rows,parameters_path,output,*,stage_callback=None):
    output=Path(output)
    if any(float(r['JD'])>=STOP for r in rows):raise ValueError('reserved row rejected before evaluation')
    if hashlib.sha256(Path(parameters_path).read_bytes()).hexdigest()!=PARAMETER_SHA256:
        raise ValueError('frozen parameters changed')
    parameters=json.loads(Path(parameters_path).read_text())
    (output/'frozen_parameters.json').write_bytes(Path(parameters_path).read_bytes())
    ledgers,evidence,concordance=ledger_concordance(rows,output)
    if stage_callback:stage_callback('concordance_passed')
    variants={}
    bundles={}
    for name,_,_,_,delay,joint in VARIANTS:
        bundle=DirectionalBundle.from_dict(parameters[name]);bundles[name]=bundle
        part=[r for r in bundle.scores(ledgers[delay],evidence[delay]) if r['M0'] is not None]
        if joint:
            ids={f['emission_index'] for f in ledgers[delay] if joint_valid(f)}
            part=[r for r in part if r['emission_index'] in ids]
        for row in part:row['gain_M2_M0']=row['M2']-row['M0']
        if not part and name=='primary':raise ValueError('no score-eligible primary evaluation forecasts')
        variants[name]=part
        write(output/(name+'-scores.json'),part)
        if name=='primary':
            primary=cluster_interval(part,'gain_M3_M2',START,6)
            primary.update(df=primary['blocks']-1,issued=len(ledgers[0.]),
                           reference_gain=REFERENCE_GAIN,upper_below_reference=primary['upper']<REFERENCE_GAIN,
                           routes={m:dict(Counter(r[m+'_route'] for r in part)) for m in ('M0','M2','M3','P3')},
                           scope='single confirmatory frozen-parameter comparison; observational-time retrospective')
            write(output/'primary.json',primary)
            if stage_callback:stage_callback('primary_written')
    return ledgers,evidence,concordance,variants,bundles


def secondary_diagnostics(ledgers,evidence,variants,bundles):
    from .evaluation_association import evaluation_association
    results={'robustness':{},'era_split':{},'inventory':{},'failures':[]}
    for name,part in variants.items():
        try:results['robustness'][name]={field:cluster_interval(part,field,START,6) for field in COMPARISONS}
        except ValueError as exc:results['robustness'][name]={'status':'not_estimable','reason':str(exc),'n':len(part)}
    results['robustness']['primary_three_year']=cluster_interval(variants['primary'],'gain_M3_M2',START,3)
    for label,start,stop in (('1960_1992',START,ERA_BOUNDARY),('1993_2017',ERA_BOUNDARY,STOP)):
        part=[r for r in variants['primary'] if start<=r['issue_time']<stop]
        try:results['era_split'][label]=cluster_interval(part,'gain_M3_M2',start,6)
        except ValueError as exc:results['era_split'][label]={'status':'not_estimable','reason':str(exc),'n':len(part)}
    groups={str(i):{'issued':0,'scored':0,'evidence':Counter(),'routes':{m:Counter() for m in ('M0','M2','M3','P3')}}
            for i in range(10)}
    outcomes={e['emission_index']:e for e in evidence[0.]}
    scored={r['emission_index']:r for r in variants['primary']}
    for feature in ledgers[0.]:
        key=str(int((feature['issue_time']-START)//(6*365.25)))
        group=groups.setdefault(key,{'issued':0,'scored':0,'evidence':Counter(),'routes':{m:Counter() for m in ('M0','M2','M3','P3')}})
        group['issued']+=1
        outcome=outcomes[feature['emission_index']];group['evidence'][outcome['kind']+':'+outcome['reason']]+=1
        row=scored.get(feature['emission_index'])
        if row:
            group['scored']+=1
            for model in group['routes']:group['routes'][model][row[model+'_route']]+=1
    results['inventory']=groups
    for label,callback in (
        ('association',lambda:evaluation_association(ledgers[0.],evidence[0.],STOP)),
        ('calibration',lambda:calibration_summary(bundles['primary'],ledgers[0.],evidence[0.])),
        ('standardized_features',lambda:standardized_feature_summary(bundles['primary'],ledgers[0.]))):
        try:results[label]=callback()
        except Exception as exc:
            results[label]={'status':'failed','error_type':type(exc).__name__,'reason':str(exc)}
            results['failures'].append(label)
    results['interpretation']='all association/robustness/era/calibration outputs are secondary; none replaces the single primary test'
    return results
