# R2 v0 independent contract audit

Codex delegate, 9 November 2026. Base: `03f4cf8`. Read only the draft, frozen
extraction/cluster code and prior R1 contract audit. No real magnitudes,
per-issuance results, archive requests, other-star observations, or SS Cyg
2018+ data/counts/coverage were read. Only `outputs/r2_contract_audit/` was
written. `counterexamples.py` and `checks.json` use invented numbers.

**Recommendation: amend, then freeze.** The resolved-event containment bounds
and formal CAR theorem are useful. The observational justification, censoring
target, DF interpretation and finite-cluster power claims need the corrections
below. None requires stopping gain-free implementation.

## 1. Separate A0, A1 and A2

- **A0: association, completeness and risk set.** The selected episode is the
  intended next qualifying latent event; no earlier qualifying onset was missed;
  the current episode is genuinely completed and the next onset is after issue.
  State the latent event's crossing/re-crossing convention independently of the
  reports used to detect it.
- **A1: containment and surviving-censor statements.** Conditional on A0 and a
  valid measurement/temporal-aggregation interpretation, T lies in its stated
  interval, or exceeds a declared censor cutoff. These are assumptions, not
  consequences of a one-magnitude report margin.
- **A2: full observation CAR/ignorability.** The kernel for the complete selected
  report object, including association, availability, stopping and selection,
  factors as K(Y|t,H,S)=c(Y,H,S)1{t in A(Y)}, with distinct forecast/observation
  parameters and a normalized kernel. This is stronger than a story about
  first decisive detection.

**A1 can fail with exact photometry.** For a continuous path linear between
(t,m)=(0,11.5),(1,9.5),(2,11.5),(3,8.5), the first magnitude-ten crossing is
T=0.75; the proposed last-faint/first-decisive-bright window is (2,3]. Every
individual report is exact. The phrase "and then reaches decisive brightness"
does not specify whether the intervening reversal disqualifies the first
crossing. Even after that ambiguity is fixed, missed/merged episodes and
physical quiescence versus one faint instant require A0. A one-magnitude error
is therefore not necessary for failure as currently defined.

`visits` independently takes median time and magnitude. Three exact reports
(0,11),(.05,8),(.1,11) become a faint visit (.05,11) even though the actual
brightness at .05 is 8. A report margin does not turn the representative visit
into an exact latent state. Conservative support times help: use the earliest
raw time supporting a selected faint visit for L and latest raw time supporting
a bright visit for U, retain the representative times separately, and still
condition containment on A0 and valid raw state/limit interpretation. The
parent's proposed raw-support implementation addresses this aggregation issue.

Contradictory decisive reports are descriptive checks, not a calibrated failure
probability. Common observer bias can produce agreement but incorrect states;
noise away from transitions need not equal noise near transitions. Do not infer
an expected number of failed onset brackets from the contradiction rate without
an explicit, validated error/association model.

## 2. What the deterministic bounds actually bound

For fixed positive conditional calendar densities g_D,g_B, h(t)=log(g_D/g_B),
and a genuinely contained resolved T, inf_{(L,U]} h <= h(T) <= sup_{(L,U]} h.
No CAR assumption is needed for that pointwise fact. Use inf/sup, because the
lower endpoint is open. Under common-origin lognormal forecasts with a fixed
common variance per issue, h is affine in log(t-anchor), so endpoint limits
supply the extrema exactly; no arbitrary time-grid approximation is needed.

**Censor survival contrast is not an exact unknown point-density contrast.**
For exponential D/B rates 2/1 and censor c=1, the survival contrast is -1.
If the actual event occurs at T=10, the point contrast is log(2)-10=-9.30685.
Thus v0's combined resolved bounds plus exact censored survival contrasts do
not bound the fully observed latent point log-score gain over all issuances.
Lognormal tail point bounds can be unbounded when the mean shift is nonzero.

A precise useful alternative is a **fixed-C mixed event-density/survival target**:
for latent T, score h(T) if T<=C, and s(C)=log S_D(C)-log S_B(C) if T>C, with
survival conditioning included once in both densities and survivals. Under A1:

| Contained interval | Deterministic mixed-score bounds |
|---|---|
| U<=C | inf/sup h over (L,U] |
| L>=C | exact s(C) |
| L<C<U | min/max of h over (L,C] and s(C) |

A no-candidate censor requires an explicit valid T>C assumption. Merely finding
a faint report at c does not prove that no earlier onset occurred and faded.
Backing censoring off to last-faint c' changes the information/score policy; it
must be declared and does not solve the survival/completeness premise. These
mixed bounds remain pointwise valid without CAR but the score's latent-
distribution propriety still requires the observation/stopping kernel.

## 3. Formal CAR proof valid; the timing narrative does not establish it

Under the stated normalized CAR kernel, p_F(Y)=c(Y)F(A(Y)); the expected score
difference relative to truth is -KL(p_F0 || p_F). Hence the coarsened log score
is proper, generally not strictly proper for latent F. The draft's derivative
argument reaches the same valid conclusion. Preserve that theorem conditional
on its full premises rather than call the real score established proper.

Neither absence of a decisive bright report nor the proposed rate checks proves
those premises. Nondecisive continuous values can guide inspection/reporting;
validation, detectability, limits and episode selection can depend on latent
shape. Sampling ignorable for a full trajectory model need not be CAR after
reducing observations to a scalar-onset interval. Conversely, adapting to truly
observed coarsened past states can remain CAR. A raw visit-rate difference is
not itself a test of CAR.

Selection matters for the proposed diagnostics: even homogeneous Poisson
inspection of an exact event has no visits strictly between its last negative
and first positive inspection, by construction. Comparing this selected gap
with an unselected five-day background will show a difference without alerts.
Report diagnostics descriptively or calibrate their null distribution under a
fully specified observation process; do not interpret short gaps as proof of
alert-driven follow-up or confine every effect to a harmless sub-bracket scale.

An observable first-report time is a legitimate operational target with different
scientific scope; it is not universally a worse statistical target. Selecting
latent onset commits the study to stronger measurement/association assumptions.

## 4. DF removes a numerical estimate, not observation/landmark pathways

DF can demonstrate that its new code path does not reuse the fitted threshold
end estimate. It is a valuable proxy/anchor comparison. But an exact observed
timestamp is still a random, potentially cadence-dependent proxy for the true
end. Disjoint reports need not have independent measurement/selection errors.

The invented-number check holds true event duration fixed at 10 and future
quiet gap Q~Uniform(30,50), independent of observing regime. Dense versus sparse
cadence yields first-faint lags 1 versus 5 and observed bright spans 8 versus 4.
All reports are exact and no numerical end estimate appears. A common-variance
lognormal baseline with a constrained positive standardized-log-span offset has
population beta=0.05549 and expected conditional score gain **+0.05395 nats**.
The mark corrects cadence-dependent anchor lag; no physical duration effect is
present. Exact calculations and survival conditioning are in `checks.json`.

Therefore a positive DF result cannot rule out observation/landmark information
as the sole explanation of an original gain. A nonpositive result cannot make
endpoint artefact the leading explanation either: the proxy, origin, sample,
information and model have changed. Fixed 0.5/0.25 ratios are descriptive
thresholds, not mechanism-identification tests. Ratios need identical outcomes,
forecasts and populations, a clearly positive denominator, and uncertainty;
prefer absolute paired contrasts when denominators are small.

Fluence is another useful measured proxy, but no general theorem says disc
memory must give it at least the predictive information in duration. Optical
relative fluence is not bolometric disc mass. Keep mechanistic comparisons
conditional on explicit physical and measurement models.

## 5. Inference: deterministic ordering is not a CR1 coverage guarantee

A1 gives ordering of realized sample means. If a lower confidence procedure
actually covers E[ell] at 95%, ordering E[ell]<=E[h] transfers that lower
coverage to E[h]. CR1/t itself is not automatically a valid conservative
procedure with few dependent clusters, fitted nuisance quantities or adaptive
weights. Separate the sure sample containment statement from approximate
population inference and from the already exploratory status of SS Cyg.

A tiny counterexample: ten nominal clusters share one common equiprobable +/-1
shock. Every cluster mean equals that shock, CR1 SE is zero, and the one-sided
positive declaration occurs 50% under true expected gain zero. The issue is
cross-cluster dependence, not a defective containment bound. Star-by-six-year
clusters require an argued dependence horizon; blocks of the same star may
share slow state and training uncertainty. Validate the chosen inference under
those processes instead of calling a block count a certification. The primary
source guide explicitly treats cross-cluster independence, large cluster
asymptotics and few-cluster complications ([Cameron & Miller 2015, sections
I–II and VI](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015.pdf)).

## 6. Power arithmetic and weighting

The draft's fixed-SD normal arithmetic is correct: effective SD=0.1327263 gives
N=400.05,1089.14,1701.78 for gains .0165,.010,.008 at one-sided 5% and 80%
power. These are conditional planning approximations, not measured model power.
They do not include finite-cluster critical values, unequal weights, star
heterogeneity, development fitting or observation qualification.

The proposed later scaling "gain SD scales with beta" changes that extrapolation:
if mean gain scales with beta squared, SD scales with sqrt(gain), making N
approximately inverse in gain, not inverse squared. Anchored at .0165, the same
arithmetic gives N=660.08 for .010 and 825.10 for .008. Neither scaling is a
universal law under misspecification; simulate an explicit full forecasting
DGP and report both planning assumptions/sensitivity rather than certify 1100.

A 40% per-star cap requires at least three eligible stars. A single downweight
followed by renormalization can violate the cap again. Define weights, e.g.
w_s=min(.4,k*n_s) with k chosen to make sum w_s=1; within-star issuance weights
w_s/n_s. Call this capped forecast weighting. Validate weighted cluster variance
and effective sample size; N observations is not N equally weighted independent
forecasts. Predeclare a minimum eligible cohort and an infeasibility rule.

One prospectively fixed primary permits a single test, but the comparator
selection algorithm must be fixed before future-star outcomes. Do not choose a
weaker comparator after seeing duration lose against the stronger one, then
keep claiming improvement beyond the strongest stable baseline. A weak/negative
ratio cannot by itself identify duration as only a slow-state indicator.

## 7. Freeze-ready interpretation

- Correct X5 report selection in a new version, preserving frozen X4 and old
  result bytes. Keep candidate detection and conservative report supports
  explicit, with limits, ties, faint peaks and missing-bound statuses tested.
- Freeze A0/A1/A2 and a mixed-score versus resolved-point target distinction.
  A conditional CAR theorem is not empirical closure of E1. Positive A1 sample
  bounds establish conditional sample ordering; population claims remain
  dependent on calibrated inference assumptions.
- DF is an anchor/proxy robustness comparison, not a binary causal gate. State
  filter clocks, missing-cycle handling, measurement approximation and whether
  the duration arm shares the timing-only filter must be explicit. A point-gap
  Kalman update is a working measurement approximation, not exact interval-
  censored state-space inference.
- R2a/c can proceed gain-free. Real R2b scores follow a concrete frozen protocol
  and review; no new-star/2018+ access or manuscript rewriting follows from
  these mathematical corrections.

No source edits, fits or real scoring were performed. The two PDF references
from the prior R1 audit were not newly reread here; Gill's URL returned 403.
The CAR argument above was checked directly from the normalized kernel.

Next: Codex — incorporate these amendments before the R2 freeze and gain-free implementation.
