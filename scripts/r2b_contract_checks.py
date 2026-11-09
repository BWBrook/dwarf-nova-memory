"""Independent invented-number R2b contract checks; no real inputs, fits or scores."""
import argparse,json,math,hashlib,sys
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.special import log_ndtr
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from dnmem.extract_x5 import x5_episodes
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output",type=Path,required=True)
args=parser.parse_args()
OUT=args.output
OUT.mkdir(parents=True,exist_ok=False)
rows=[]
for j,(t,m,who) in enumerate([(0,9.5,'invented-A'),(.05,11.5,'invented-A'),(.10,11.5,'invented-A'),(.01,9,'invented-B'),(1,8.5,'invented-C'),(2,8,'invented-D'),(3,11.5,'invented-E')]):
    rows.append(dict(obsID=str(j),JD=t,mag=m,fainterThan='0',obsName=who,by=who,band='Vis.',val='V'))
episodes=[dict(peak_t=-3,peak_mag=8,confirmed_event=True),dict(peak_t=2,peak_mag=8,confirmed_event=True)]
e=x5_episodes(rows,episodes=episodes)[1]
assert e['onset_report_eligible'] and e['onset_report_lo']==0 and e['onset_report_hi']==1
mu=math.log(40);sigma=.4
J=(1+sigma*sigma)*math.exp(2*sigma*sigma-2*mu)/(sigma*sigma)
def kl(age,delta):
    if delta>age:
        return {'exact_KL':'infinite','reason':'P has positive mass where shifted Q has zero support'}
    za=(math.log(age)-mu)/sigma
    lp=float(log_ndtr(-za));lq=float(log_ndtr(-(math.log(age-delta)-mu)/sigma)) if age>delta else 0
    def integrand(z):
        x=math.exp(mu+sigma*z);y=x-delta
        a=-.5*z*z-math.log(x*sigma)-.5*math.log(2*math.pi)
        b=-.5*((math.log(y)-mu)/sigma)**2-math.log(y*sigma)-.5*math.log(2*math.pi)
        return math.exp(-.5*z*z-.5*math.log(2*math.pi)-lp)*(a-b+lq-lp)
    value,error=quad(integrand,za,12,epsabs=1e-13,epsrel=1e-10)
    approximation=.5*J*delta*delta
    return dict(exact_KL=value,quadrature_error=error,local_unconditional_index=approximation,ratio=value/approximation)
klchecks=[dict(issue_age=age,shift=delta,**kl(age,delta)) for age,delta in [(0,.1),(2,.1),(2,1),(10,9)]]
assert klchecks[2]['exact_KL']>klchecks[2]['local_unconditional_index']
# Independent direct Gaussian covariance: local level random walk plus stationary AR(1).
phi=.4;sL=.03;sAR=.3;n=4
C=np.array([[1+min(i+1,j+1)*sL*sL+sAR*sAR*phi**abs(i-j)/(1-phi*phi) for j in range(n)] for i in range(n)])
weights=np.linalg.solve(C[:3,:3],C[:3,3])
assert abs(weights[0])>1e-6
result=dict(scope='invented numbers only; no real data, fit or original forecast score',
    aggregation_counterexample=dict(raw_reports=[{k:r[k] for k in ['JD','mag','obsName']} for r in rows],
        latent_path_vertices=[[-2,11.5],[-1,11.5],[-.1,10],[0,9.5],[.01,9],[.05,11.5],[.10,11.5],[1,8.5],[2,8],[3,11.5]],
        previous_qualifying_end=-2,first_latent_decisive_time=.01,last_rising_threshold_crossing_before_first_decisive=-.1,
        no_decisive_excursion_before_raw_L=True,all_reports_exact=True,x5_window=[e['onset_report_lo'],e['onset_report_hi']],
        x5_eligible=e['onset_report_eligible'],x5_flags=e['onset_flags'],target_contained=False,
        implication='The explicit v0 A0 condition before raw L is insufficient; a faint witness ordered before first decisive brightness is additionally needed.'),
    additive_shift_Fisher_checks=dict(median=40,sigma=sigma,unconditional_J=J,rows=klchecks),
    state_history_sensitivity=dict(phi=phi,level_sd=sL,ar_sd=sAR,three_history_predictive_weights=weights.tolist(),
        oldest_log_gap_perturbation=.1,predicted_log_location_shift=float(.1*weights[0]),last_gap_change=0,
        implication='A derivative with respect only to the most recent gap omits older measured-history errors.'),
    source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['docs/protocols/r2b-execution-v0.md','src/dnmem/extract_x5.py','src/dnmem/r2_models.py','src/dnmem/r2_scores.py']})
(OUT/'checks.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
print(json.dumps({'aggregation_eligible_but_uncontained':True,'KL_fixture':klchecks[2],'history_weights':weights.tolist()}))
