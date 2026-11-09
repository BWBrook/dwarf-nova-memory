# Independent R2d design and prefreeze implementation review

Codex delegate, 9 November 2026. Read Claude's R2d v0 in full, the R2b review
and its checking script, then the proposed v1, sequential simulation module,
runner, grid and focused tests. The delegate saw the design and implementation;
this is an independent derivation and code-path review, not blindness to them.
No real fit, real forecast score, simulation grid or archive request was run.
Only invented-number arithmetic was executed. Public source hashes are saved
in `data/provenance/r2d_review_audit/design-checks.json`.

**Verdict:** v1 is defensible as a bounded dual-statistic precision screen.
No blocking implementation error was found in the reviewed point-Gaussian
experiment. It cannot certify X5/window/calendar inference or authorize data
access. Forecast gain remains the default future confirmatory claim; replacing
it with a score-moment claim needs an explicit scientific decision.

## Mathematical conclusions and amendments to v0

1. **Positive score is not positive frozen-rule gain.** In a unit-variance
   Gaussian example with standardized mark x, true mean beta*x and frozen
   candidate shift b*x, expected score at zero is beta, while candidate gain
   is b*beta-b²/2. Beta=.05 and b=.20 give score +.05 but gain -.010 nats.
   At 5,000 balanced unit marks the score noncentrality is 3.536. A better
   association test need not validate the actual trained forecast. The v1
   dual-statistic distinction corrects v0's primary-test switch.

2. **Rolling guards do not remove common trends by construction.** If mark
   means drift a per event and gap means b, subtraction of ten past marks
   leaves 5.5a and a twenty-residual mean correction leaves 10.5b in a simple
   Gaussian mean example. The score expectation is 57.75ab. With a=.02 and
   b=.01 it is .01155; a frozen coefficient .1 gains .0010945 despite no
   direct mark effect. That is real information over a lagging baseline,
   hence a specificity stress, not a strict predictive-null false positive.
   Rolling operations also induce dependence: independent iid mark/error
   streams have covariance -h/10² and -h/20² at lag h≤10 after guarding;
   their score covariance is the positive product. The simulator must
   reproduce sequential guards rather than multiply iid variance by a scalar.

3. **Nuisance efficiency requires an argument.** Causal mark centering,
   centering the variance estimate and nuisance orthogonalization are
   different operations. A regular efficient score subtracts
   I(beta,theta) I(theta,theta)^-1 U(theta). Development-estimated parameters
   and adaptive recalibration also contribute estimation uncertainty.
   Gaussian intercept/mark cross-information is proportional to E[x], which
   the trend fixture leaves nonzero. Cluster variance adjustment cannot
   remove a nonzero moment from baseline error. V1 correctly studies a
   score-type moment and refits the whole learning algorithm per trial.

4. **Few-star inference has a real information limit.** Whole-star clustering
   addresses within-star serial dependence, but assumes independent stars;
   common observing/archive eras can violate it. Exact Rademacher sign flips
   additionally require symmetric star contributions. Their minimum one-sided
   p is 2^-S: .125 for three stars, .0625 for four and .03125 for five.
   More forecasts or bootstrap draws cannot overcome the first two cases.
   CR1/t and sign flips are declared candidates, not finite-sample guarantees.

5. **Individual KL is not pooled signal.** Equally weighted slopes +.126 and
   -.126 have mean individual oracle KL .007938 but pooled score zero and
   optimal shared coefficient zero. The relation delta=sqrt(2 KL) is local
   to a correctly specified optimal comparison; achieved frozen-rule gain,
   mark noise, centering, development learning and coarsening change it. The
   v0 .0085 row was also mislabeled: Claude's table gives about .0052 for
   guarded DF B2 and .0086 for DF B0. V1 replaces this with explicitly nominal
   input signal and records achieved targets.

## Availability, censoring and interpretation contracts still open

The saved R2b final-window endpoint is not by itself the time its complete
label became knowable. Candidate confirmation, recrossings, peak identity,
window eligibility and recognized coverage loss can require later reports.
Future observational recalibration needs prefix outcome versions or a declared
conservative stopping rule. Historical data-release dates also remain unknown.
The proposed development warm start differs from the R2b review script's
evaluation-only residual history and is a new rule. V1 discloses both points.

Independent delayed point labels do not test informative censoring, missed
outbursts, observer-triggered visits or interval-likelihood assumptions.
Neither strict-null calibration nor the absence of a direct physical mark
effect makes these observational mechanisms ignorable. The present screen is
deliberately conditional on the point-Gaussian construction, not the final
multi-star execution gate.

B2's worse development fit is descriptive; it does not uniquely diagnose the
physical cause. Choosing B0R for simplicity is a disclosed post-R2b amendment;
choosing it because its observed gain is smaller would still use results.
Changing both mark and baseline does not identify a causal fraction of gain
due to era drift. C01 has not been recomputed under these guards. A positive
rate estimate becoming inconclusive does not establish its absence. These
qualifications govern C61–C64 and any later product rewrite.

## Bounded implementation review

Reviewed `src/dnmem/r2d_simulation.py`, `scripts/r2d_precision.py`,
`data/provenance/r2d_precision/design.json`, v1 and the focused tests.

- Development outcomes used in fitting must be available by the development
  cutoff. Evaluation history and residual recalibration use available labels
  only; current outcomes cannot enter their own forecast. Nonmonotone arrivals
  select the latest issuance indices among available labels, as declared.
  Development residual reference predictions use the final development fit
  retrospectively; v1 explicitly avoids calling them historical issued fits.
- The Gaussian score/gain identities and innovation variance are coherent.
  The generator's conditional means support exact per-step predictable
  expectations. Their realized-path average is not unconditional long-run KL
  and is not an expectation conditional on the entire realized future path.
- The oracle-null arm knows the latent mean and innovation variance and
  disables estimated recalibration. This provides a strict predictive-null
  control. Estimated-base no-direct-effect cases may genuinely gain.
- Development and evaluation capped star weights are applied separately and
  normalized. Missing marks return the exact baseline; fewer than three
  development contributors give zero offset. Guarded effects and the Gaussian
  offset are not asserted to equal the original interval-model parameter fit.
- Nominal epochs are equal-count bins; their halves are not actual eighteen-year
  clusters. Cross-star stresses are useful failure cases, not independent-star
  inference guarantees. The grid has 35 fixed cases with 2,000 new deterministic
  seeds per case and reports all predeclared methods without choosing one.
- Exact Monte Carlo intervals, failures and zero-offset trials are retained;
  nonidentity coverage is reported separately. Observed ≤5% is a screen, not
  certification. Power readiness needs its lower MC limit across the admitted
  envelope and satisfactory null/coverage behavior. A failed envelope must be
  reported rather than resolved by dropping difficult cells.
- `positive_score_negative_gain_count` counts positive **predictable mean
  scores** with negative predictable mean gains. It does not count positive
  score-test detections; prose must preserve that distinction.

No source edits were made to the candidate or runner. The root agent owns full
tests, the freeze, the grid and integration. Nothing in this review permits new
archive access or physical-memory attribution.

## Checked primary method sources

The author-hosted [Pustejovsky–Tipton manuscript](https://jepusto.com/files/Pustejovsky-Tipton-201601.pdf)
was read for its independent-cluster assumptions and working-covariance CR2
construction (printed pp.6,9–10). These concern the stated linear estimator,
not a generic correction for this adaptive nonlinear moment. An official
[2023 corrigendum](https://doi.org/10.1080/07350015.2023.2174123) exists; its full
formulae were not checked in this delegate audit. The Kline–Santos full text
was inaccessible at the attempted NBER endpoint, so no full-method verification
or Kline–Santos implementation claim is made here. The root's source check is
separate. The finite-cluster and counterexample calculations above are direct
derivations, reproduced by:

```sh
python scripts/r2d_design_checks.py --output /tmp/r2d-design-checks.json
```

The retained aggregate is
`data/provenance/r2d_review_audit/design-checks.json`; the CLI refuses overwrite.
