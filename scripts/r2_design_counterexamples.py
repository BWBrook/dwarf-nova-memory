"""Invented-number checks only; no archive or real light-curve inputs."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import NormalDist
from scipy.special import log_ndtr

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=False)
HERE = args.output

# A censoring probability is not the unknown event's point density.
point = math.log(2.0) - 10.0
survival = -1.0
assert point < survival

# Exact photometry with a re-crossing defeats the stated first-crossing target.
# m(t) is linear between (0,11.5),(1,9.5),(2,11.5),(3,8.5).
first_crossing = .75
last_faint, first_decisive_bright = 2.0, 3.0
assert not last_faint < first_crossing <= first_decisive_bright

# A representative observer-visit state may never have been observed there.
# Three exact reports at t0,.05,.1 with m11,8,11 have median(m)=11,
# median(t)=.05, but the true reported brightness at .05 is8.

# Positive decoupled-forecast gain from observing cadence alone.
# True event length10 and true next quiet gap Q~Uniform(30,50) are identical
# across independent cadence regimes. Dense/sparse first-faint anchor lags1/5,
# and reported bright spans8/4, are all exact report timestamps.
def moments(a, b):
    log_first = lambda x: x * math.log(x) - x
    log_second = lambda x: x * (math.log(x) ** 2 - 2 * math.log(x) + 2)
    return ((log_first(b) - log_first(a)) / (b - a),
            (log_second(b) - log_second(a)) / (b - a))

moments_dense, moments_sparse = moments(29,49), moments(25,45)
mu = (moments_dense[0] + moments_sparse[0]) / 2
variance = (moments_dense[1] + moments_sparse[1]) / 2 - mu * mu
sigma = math.sqrt(variance)
beta = (moments_dense[0] - moments_sparse[0]) / 2
unconditional_gain = beta * beta / (2 * variance)
# Common issue age1; condition both lognormal forecasts on survival once.
logsf = lambda loc: float(log_ndtr(loc / sigma))
conditional_correction = logsf(mu) - .5 * (logsf(mu+beta) + logsf(mu-beta))
conditional_gain = unconditional_gain + conditional_correction
assert beta > 0 and conditional_gain > .01

# A1 lower scores do not give CR1 its independence/calibration premises.
# Ten nominal clusters share the same random +/-1 effect. Every observed
# cluster mean is identical, so CR1 SE0; a one-sided positive result occurs50%.

sd = .0063203 * math.sqrt(441)
z = NormalDist().inv_cdf(.95) + NormalDist().inv_cdf(.8)
fixed_variance_n = {str(delta): (z*sd/delta)**2 for delta in (.0165,.010,.008)}
scaled_variance_n = {str(delta): z*z*sd*sd/(.0165*delta) for delta in (.0165,.010,.008)}
result = {
 'scope':'Independent mathematical checks from invented numbers only; no real data or scores',
 'censor_counterexample':{'lambda_D':2,'lambda_B':1,'censor':1,'true_T':10,'survival_log_ratio':survival,'latent_point_log_ratio':point},
 'recrossing_counterexample':{'path_vertices':[[0,11.5],[1,9.5],[2,11.5],[3,8.5]],'first_threshold_crossing':first_crossing,'L':last_faint,'U':first_decisive_bright,'contains_first_crossing':False,'individual_measurement_errors':0},
 'aggregation_counterexample':{'reports':[[0,11],[.05,8],[.1,11]],'representative_visit':[.05,11],'true_magnitude_at_representative_time':8,'individual_measurement_errors':0},
 'decoupled_cadence_counterexample':{'true_duration':10,'true_gap_distribution':'Uniform(30,50), independent of cadence and mark','anchor_lags':[1,5],'observed_bright_spans':[8,4],'mu_B':mu,'sigma_B':sigma,'positive_beta_for_standardized_log_span':beta,'expected_log_score_gain':conditional_gain,'survival_correction':conditional_correction,'measurement_errors':0,'estimated_end_used':False},
 'CR1_counterexample':{'nominal_clusters':10,'cross_cluster_common_shock':'All gains equal common equiprobable +1 or -1','CR1_se':0,'true_expected_gain':0,'one_sided_false_positive_probability':.5},
 'precision_arithmetic':{'effective_sd_from_original':sd,'fixed_variance_required_N_normal_approx':fixed_variance_n,'if_score_sd_scales_as_sqrt_gain_normal_approx':scaled_variance_n,'not_certified_power':True},
 'input_source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['docs/protocols/r2-design-v0.md','src/dnmem/extract.py','src/dnmem/extract_x4.py','src/dnmem/oc_statistics.py']},
}
(HERE/'checks.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps({'positive_DF_beta':beta,'positive_DF_gain_without_end_estimate':conditional_gain,'fixed_N':fixed_variance_n,'scaled_N':scaled_variance_n},indent=2))
