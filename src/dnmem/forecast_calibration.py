"""Descriptive distribution checks for frozen landmark forecasts under censoring."""

import math
from statistics import fmean, pstdev


def predictive_cdf(bundle, feature, model, remaining):
    if remaining <= 0:
        return 0.
    outcome={'emission_index':feature['emission_index'],'issue_time':feature['issue_time'],
             'kind':'right_censored','censor_at':feature['issue_time']+remaining}
    log_survival=bundle.score(feature,outcome,model)
    if log_survival is None or math.isnan(log_survival) or log_survival > 1e-9:
        raise ValueError('invalid conditional predictive survival')
    return -math.expm1(min(0.,log_survival))


def predictive_quantile(bundle, feature, model, probability):
    if not 0 < probability < 1:
        raise ValueError('quantile probability must lie strictly between zero and one')
    lower,upper=0.,1.
    for _ in range(128):
        if predictive_cdf(bundle,feature,model,upper) >= probability:
            break
        upper*=2.
    else:
        raise ValueError('could not bracket predictive quantile')
    for _ in range(50):
        middle=(lower+upper)/2
        if predictive_cdf(bundle,feature,model,middle) < probability:lower=middle
        else:upper=middle
    return (lower+upper)/2


def coverage_class(outcome, lower, upper):
    issue=float(outcome['issue_time'])
    if outcome['kind']=='interval':
        lo,hi=float(outcome['onset_lo'])-issue,float(outcome['onset_hi'])-issue
        if lower <= lo and hi <= upper:return 'covered'
        if hi < lower or lo > upper:return 'not_covered'
        return 'undetermined'
    if outcome['kind']=='right_censored':
        return 'not_covered' if float(outcome['censor_at'])-issue >= upper else 'undetermined'
    raise ValueError('excluded evidence cannot enter calibration')


def calibration_summary(bundle, ledger, evidence):
    by_id={row['emission_index']:row for row in evidence}
    if len(by_id)!=len(evidence) or set(by_id)!={row['emission_index'] for row in ledger}:
        raise ValueError('calibration population mismatch')
    results={}
    for model in ('M0','M2','M3'):
        deciles=[0]*10
        brackets=[]
        counts={str(level):{kind:0 for kind in ('covered','not_covered','undetermined')} for level in (.5,.9)}
        n=censored=0
        for feature in ledger:
            outcome=by_id[feature['emission_index']]
            if outcome['kind']=='excluded':continue
            n+=1
            if outcome['kind']=='interval':
                lo=predictive_cdf(bundle,feature,model,float(outcome['onset_lo'])-feature['issue_time'])
                hi=predictive_cdf(bundle,feature,model,float(outcome['onset_hi'])-feature['issue_time'])
                mid=(lo+hi)/2
                deciles[min(9,int(mid*10))]+=1
                brackets.append({'emission_index':feature['emission_index'],'cdf_lower':lo,'cdf_upper':hi,'mid_cdf':mid})
            else:censored+=1
            for level in (.5,.9):
                lower=predictive_quantile(bundle,feature,model,(1-level)/2)
                upper=predictive_quantile(bundle,feature,model,(1+level)/2)
                counts[str(level)][coverage_class(outcome,lower,upper)]+=1
        for value in counts.values():
            value['n']=n
            value['coverage_lower_bound']=value['covered']/n if n else None
            value['coverage_upper_bound']=(value['covered']+value['undetermined'])/n if n else None
        results[model]={'scored':n,'resolved_onsets':len(brackets),'right_censored':censored,
                        'resolved_onset_mid_cdf_deciles':deciles,'cdf_brackets':brackets,'central_intervals':counts}
    return {'models':results,'interpretation':'resolved-onset mid-CDF deciles are descriptive under outcome selection, not a uniformity test; coverage bounds retain interval and right censoring'}


def standardized_feature_summary(bundle, ledger):
    m2,m3=bundle.models['M2'],bundle.models['M3']
    values={'q':[],'L':[],'x':[]}
    missing_L=0
    for row in ledger:
        if bundle.route(row,'M2')!='M2':continue
        values['q'].append((math.log(row['previous_gap'])-m2.centers['previous_gap'])/m2.scales['previous_gap'])
        gaps=row.get('earlier_gaps') or []
        if gaps:
            values['L'].append((fmean(gaps)-m2.centers['earlier_level'])/m2.scales['earlier_level'])
        else:
            values['L'].append(0.);missing_L+=1
        duration=row.get('duration')
        if duration is not None and duration>0:
            values['x'].append((math.log(duration)-m3.centers['mark'])/m3.scales['mark'])
    return {'features':{key:{'n':len(v),'mean':fmean(v) if v else None,'sd':pstdev(v) if v else None} for key,v in values.items()},
            'missing_L_imputed_zero':missing_L,
            'reference':'training transforms are frozen; zero/one reference applies to the original observed training predictor population, not necessarily to a selected/censored evaluation subset'}
