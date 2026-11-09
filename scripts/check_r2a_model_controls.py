"""Independent numerical audit: direct Gaussian conditioning, no dnmem imports."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse
import hashlib,json,math,statistics,subprocess
import numpy as np
from scipy.stats import lognorm

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--run",type=Path,default=ROOT/"outputs/r2a_model_controls_f0049dd")
parser.add_argument("--output",type=Path,required=True)
args=parser.parse_args()
RUN=args.run.resolve()
OUT=args.output.resolve()
OUT.mkdir(parents=True,exist_ok=False)
TOL=1e-9
inputs={};failures=[]

def read(path):
    raw=path.read_bytes();inputs[str(path.relative_to(ROOT))]=hashlib.sha256(raw).hexdigest();return json.loads(raw)

def require(ok,message):
    if not ok:failures.append(message)

def previous_ok(row):
    q=row.get('previous_gap')
    return row.get('previous_gap_covered') is True and q is not None and math.isfinite(q) and q>0

def mark_ok(row):
    value=row.get('mark')
    return value is not None and math.isfinite(value) and value>0

def values(row):
    require(row['available_at']<=row['issue_time'],'future feature')
    result=[]
    for item in row['gap_history']:
        require(item['available_at']<=row['issue_time'],'future history')
        require(item['log_gap'] is None or math.isfinite(item['log_gap']),'nonfinite history')
        result.append(item['log_gap'])
    if previous_ok(row):
        require(bool(result) and result[-1] is not None,'previous gap without last history')
        if result and result[-1] is not None:require(abs(math.log(row['previous_gap'])-result[-1])<=1e-12,'inconsistent previous gap')
    else:require(not result or result[-1] is None,'uncovered last gap not missing')
    return result

def raw_covariates(row,name,discount):
    history=values(row);older=history[:-1]
    if name=='B0':
        valid=[v for v in older if v is not None]
        return [history[-1],statistics.fmean(valid) if valid else None]
    second=older[-1] if older else None
    weighted=[(discount**position,value) for position,value in enumerate(older[::-1]) if value is not None]
    total=math.fsum(w for w,v in weighted)
    level=math.fsum(w*v for w,v in weighted)/total if total>0 else None
    return [history[-1],second,level]

def covariance_prediction(history,parameters):
    location,phi,log_level,log_ar=parameters
    level_sd,ar_sd=math.exp(log_level),math.exp(log_ar)
    def covariance(i,j):
        return 1.0+min(i,j)*level_sd**2+ar_sd**2*phi**abs(i-j)/(1-phi**2)
    observed=[i+1 for i,value in enumerate(history) if value is not None]
    target=len(history)+1
    if observed:
        matrix=np.array([[covariance(i,j) for j in observed] for i in observed])
        cross=np.array([covariance(target,i) for i in observed])
        residual=np.array([history[i-1]-location for i in observed])
        prediction=location+float(np.dot(cross,np.linalg.solve(matrix,residual)))
        variance=covariance(target,target)-float(np.dot(cross,np.linalg.solve(matrix,cross)))
    else:prediction,variance=location,covariance(target,target)
    if not variance>0:raise ValueError('nonpositive direct conditional variance')
    return prediction,math.sqrt(variance)

def base_prediction(row,name,model):
    history=values(row);issue=row['issue_time'];anchor=row['clock_anchor']
    if anchor is None:return (issue,issue,*model['remaining']),'R0'
    require(anchor<=issue,'anchor follows issue')
    if not previous_ok(row):return (anchor,issue,*model['constant']),'constant'
    if name=='B2':location,sigma=covariance_prediction(history,model['parameters'])
    else:
        raw=raw_covariates(row,name,model['discount'])
        transformed=[0.0 if value is None else (value-center)/scale for value,(center,scale,fixed) in zip(raw,model['transform'])]
        location=model['parameters'][0]+math.fsum(a*b for a,b in zip(model['parameters'][1:-1],transformed))
        sigma=math.exp(model['parameters'][-1])
    return (anchor,issue,location,sigma),name

def enriched_prediction(row,name,model,base,route,beta=None):
    coefficient=model['beta'] if beta is None else beta
    if route in ('R0','constant') or coefficient==0.0 or not mark_ok(row):return base,route
    anchor,issue,location,sigma=base
    return (anchor,issue,location+coefficient*(math.log(row['mark'])-model['mark_center'])/model['mark_scale'],sigma),name+'+D'

def score(clock,outcome):
    anchor,issue,location,sigma=clock
    age=issue-anchor
    require(age>=0,'negative age')
    denominator=float(lognorm.logsf(age,s=sigma,scale=math.exp(location)))
    if outcome['kind']=='point':
        require(outcome['onset_t']>issue,'point not after issue')
        numerator=float(lognorm.logpdf(outcome['onset_t']-anchor,s=sigma,scale=math.exp(location)))
    elif outcome['kind']=='right_censored':
        require(outcome['censor_at']>=issue,'censor before issue')
        numerator=float(lognorm.logsf(outcome['censor_at']-anchor,s=sigma,scale=math.exp(location)))
    elif outcome['kind']=='interval':
        require(issue<=outcome['onset_lo']<outcome['onset_hi'],'invalid interval')
        mass=float(lognorm.cdf(outcome['onset_hi']-anchor,s=sigma,scale=math.exp(location))-lognorm.cdf(outcome['onset_lo']-anchor,s=sigma,scale=math.exp(location)))
        if mass<=0:raise ValueError('unresolved independent interval mass')
        numerator=math.log(mass)
    else:raise ValueError('unsupported evidence')
    answer=numerator-denominator
    if not math.isfinite(answer):raise ValueError('nonfinite independent score')
    return answer

def check_training(data,label):
    rows={r['emission_index']:r for r in data['features']}
    pairs=[(rows[e['emission_index']],e) for e in data['training_evidence'] if e['kind']!='excluded']
    cutoff=data['summary']['meta']['training_cutoff']
    for row,e in pairs:
        require(row['issue_time']<cutoff,label+' training issue after cutoff')
        require(e['computed_as_of']<=cutoff and e['evidence_available_at']<=cutoff,label+' training label availability after cutoff')
        support=e['onset_hi'] if e['kind']=='interval' else e['censor_at'] if e['kind']=='right_censored' else e['onset_t']
        require(support<=min(e['computed_as_of'],e['evidence_available_at']),label+' outcome support after availability')
    anchored=[(r,e) for r,e in pairs if r['clock_anchor'] is not None]
    timed=[(r,e) for r,e in anchored if previous_ok(r)]
    marked=[(r,e) for r,e in timed if mark_ok(r)]
    counts=Counter();errors={};transform_errors=[]
    for name,model in data['models'].items():
        if name!='B2':
            raw=[raw_covariates(row,name,model['discount']) for row,e in timed]
            for position,stored in enumerate(model['transform']):
                valid=[v[position] for v in raw if v[position] is not None]
                center=statistics.fmean(valid) if valid else 0.;spread=statistics.pstdev(valid) if valid else 0.
                fixed=not valid or spread<=1e-10;scale=1. if fixed else spread
                transform_errors.extend([abs(center-stored[0]),abs(scale-stored[1])]);require(fixed==stored[2],label+' transform fixed flag')
        mark_values=[math.log(r['mark']) for r,e in marked]
        require(abs(statistics.fmean(mark_values)-model['mark_center'])<=TOL,label+' mark center')
        require(abs(statistics.pstdev(mark_values)-model['mark_scale'])<=TOL,label+' mark scale')
        objectives={}
        for key,group,remaining in [('remaining_fit',pairs,True),('constant_fit',anchored,False)]:
            total=0.
            for row,e in group:
                clock=(row['issue_time'] if remaining else row['clock_anchor'],row['issue_time'],*model['remaining' if remaining else 'constant'])
                total-=score(clock,e);counts[e['kind']]+=1
            objectives[key]=total
        base_total=mark_total=zero_total=0.
        for row,e in timed:
            clock,route=base_prediction(row,name,model);base_total-=score(clock,e);counts[e['kind']]+=1
            if mark_ok(row):
                enriched,enriched_route=enriched_prediction(row,name,model,clock,route)
                mark_total-=score(enriched,e);zero_total-=score(clock,e);counts[e['kind']]+=2
        objectives['base_fit']=base_total
        for key,total in objectives.items():errors[name+':'+key]=abs(total-model['metadata'][key]['objective'])
        if model['metadata']['offset_fit']['status']=='optimized':
            errors[name+':offset_fit']=abs(mark_total-model['metadata']['offset_fit']['objective'])
            errors[name+':zero_offset_objective']=abs(zero_total-model['metadata']['offset_fit']['zero_objective'])
    if transform_errors:require(max(transform_errors)<=TOL,label+' transform mismatch')
    for key,value in errors.items():require(value<=TOL,label+' objective mismatch '+key)
    return {'objective_maximum_absolute_error':max(errors.values()),'objective_components_checked':len(errors),'training_score_terms_by_kind':dict(counts),'maximum_transform_error':max(transform_errors,default=0.)}

receipt=read(RUN/'receipt.json')
require(receipt['status']=='completed' and not receipt['failures'],'input batch not completed cleanly')
for name,expected in receipt['files_sha256'].items():
    require(hashlib.sha256((RUN/name).read_bytes()).hexdigest()==expected,'receipt hash mismatch '+name)
for name,expected in receipt['source_sha256'].items():
    require(hashlib.sha256(subprocess.check_output(['git','show',receipt['freeze_commit']+':'+name],cwd=ROOT)).hexdigest()==expected,'historical source hash mismatch '+name)
all_summaries=[];score_errors=[];gain_errors=[];zero=0;exact_saved=0;reason_counts=Counter();route_counts=Counter();per_history=[]
for file in sorted(RUN.glob('*-00?.json')):
    data=read(file);label=file.stem;features={r['emission_index']:r for r in data['features']};truth={r['emission_index']:r for r in data['truth']}
    require(len(features)==len(data['features']) and len(truth)==len(data['truth']),label+' duplicate feature/truth IDs')
    model_values=defaultdict(list);history_errors=[]
    for saved in data['scores']:
        index=saved['emission_index'];row=features[index];outcome=truth[index]
        require(row['issue_time']==saved['issue_time']==outcome['issue_time'],label+' issue alignment')
        for name,model in data['models'].items():
            base,route=base_prediction(row,name,model);enriched,marked_route=enriched_prediction(row,name,model,base,route)
            forced_zero,zero_route=enriched_prediction(row,name,model,base,route,beta=0.)
            require(forced_zero==base and zero_route==route,label+' zero nesting');zero+=1
            actual=saved[name];require(actual['base_route']==route and actual['mark_route']==marked_route,label+' route mismatch '+name)
            plain,marked=score(base,outcome),score(enriched,outcome)
            for expected,value in ((actual['base'],plain),(actual['marked'],marked)):
                error=abs(expected-value);score_errors.append(error);history_errors.append(error);require(error<=TOL,label+' score mismatch '+name)
            error=abs(actual['gain']-(marked-plain));gain_errors.append(error);require(error<=TOL,label+' gain mismatch '+name)
            if marked_route==route:
                require(actual['base']==actual['marked'] and actual['gain']==0.,label+' exact saved identity mismatch');exact_saved+=1
            reason='missing_anchor' if route=='R0' else 'missing_previous_gap' if route=='constant' else 'zero_beta' if model['beta']==0. else 'missing_mark' if not mark_ok(row) else 'marked'
            reason_counts[reason]+=1;route_counts[name+':'+marked_route]+=1
            model_values[name].append((plain,marked-plain))
    for name,rows in model_values.items():
        mean_gain=statistics.fmean(r[1] for r in rows);mean_base=statistics.fmean(r[0] for r in rows)
        require(abs(mean_gain-data['summary']['rungs'][name]['mean_gain'])<=TOL,label+' mean gain '+name)
        require(abs(mean_base-data['summary']['rungs'][name]['mean_base_log_density'])<=TOL,label+' mean base '+name)
        all_summaries.append({'case':data['summary']['meta']['case'],'rung':name,'mean_gain':mean_gain,'beta':data['models'][name]['beta']})
    per_history.append({'history':label,'evaluation_rows':len(data['scores']),'maximum_score_error':max(history_errors),'training':check_training(data,label)})
aggregate=read(RUN/'summary.json');aggregate_errors=[]
for row in aggregate['rows']:
    selected=[r for r in all_summaries if r['case']==row['case'] and r['rung']==row['rung']];mean=statistics.fmean(r['mean_gain'] for r in selected);se=statistics.stdev(r['mean_gain'] for r in selected)/math.sqrt(len(selected))
    aggregate_errors.extend([abs(mean-row['mean_gain']),abs(se-row['mc_se'])]);require(sum(r['beta']>0 for r in selected)==row['positive_offsets'],'positive offset count')
require(max(aggregate_errors)<=TOL,'aggregate mean/MCSE mismatch');require(zero==aggregate['exact_zero_nesting_checks']==3240,'zero nesting count');require(len(per_history)==9,'not all9histories')
inputs[str(Path(__file__).relative_to(ROOT))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
for name,expected in inputs.items():require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,'inspected input changed '+name)
report={'status':'failed' if failures else 'passed','absolute_tolerance':TOL,'histories_checked':len(per_history),'evaluation_score_terms':len(score_errors),'evaluation_gain_terms':len(gain_errors),'maximum_score_error':max(score_errors),'maximum_gain_error':max(gain_errors),'maximum_aggregate_mean_or_mcse_error':max(aggregate_errors),'zero_counterfactual_predictions':zero,'exact_saved_zero_or_missing_pairs':exact_saved,'routing_counts':dict(route_counts),'identity_or_enrichment_reasons':dict(reason_counts),'training_score_terms_by_kind':dict(sum((Counter(r['training']['training_score_terms_by_kind']) for r in per_history),Counter())),'maximum_training_objective_error':max(r['training']['objective_maximum_absolute_error'] for r in per_history),'maximum_transform_error':max(r['training']['maximum_transform_error'] for r in per_history),'per_history':per_history,'failures':failures,'input_sha256':inputs,'prediction_derivation':'B0/B1 reconstructed from saved transforms and raw prefix histories; B2 direct joint Gaussian covariance conditioning, not candidate Kalman recursion','score_derivation':'SciPy lognorm logpdf/logsf/CDF differences conditional on survival to issue; no dnmem imports','limits':['No fits, optimizer validation, new simulation or real observations.','Synthetic evaluation outcomes are points; retained mixed training outcomes independently verify point/interval/censor objectives.','Zero-counterfactual predictions are independently reconstructed; original candidate zero-nesting calls were not rerun.','Nine finite controls and numerical agreement do not establish calibration, identifiability or physical validity.']}
(OUT/'summary.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
(OUT/'report.md').write_text('# Independent R2 model-control score audit\n\n'+f"Status: {report['status']}; tolerance {TOL:g}; {len(failures)} failures.\n\n"+f"All nine histories: {len(score_errors):,} evaluation base/marked scores agree within {max(score_errors):.3g}; {len(gain_errors):,} paired gains within {max(gain_errors):.3g}. Aggregate means and MC SEs agree within {max(aggregate_errors):.3g}.\n\n"+f"Independent direct Gaussian covariance conditioning replaces the candidate B2 Kalman recursion. B0/B1 transforms, missing-history conventions and mark scaling are reconstructed. SciPy lognormal density/survival/CDF scores verify all outcome kinds in retained training objectives (maximum objective error {report['maximum_training_objective_error']:.3g}).\n\n"+f"There are {zero:,} independent zero-counterfactual predictions and {exact_saved:,} exact saved zero/missing pairs. Routes and availability checks agree. Input hashes are in summary.json. No candidate scoring/prediction function was imported; no fit or simulation was run. This is a numerical audit of finite synthetic controls, not calibration or identification.\n")
print(json.dumps({k:report[k] for k in ('status','histories_checked','evaluation_score_terms','maximum_score_error','maximum_gain_error','maximum_training_objective_error','maximum_aggregate_mean_or_mcse_error','exact_saved_zero_or_missing_pairs','training_score_terms_by_kind','failures')}))
raise SystemExit(bool(failures))
