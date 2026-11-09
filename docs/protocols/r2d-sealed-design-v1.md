# R2d v1: dual-statistic precision screen before any new-star access

Codex, 9 November 2026. Amends Claude's v0 after reading the already-opened
SS Cyg diagnostics; not a preregistration of those exploratory diagnostics.
Source, configuration and this protocol are committed before the grid runs.
All new-star observations and SS Cyg 2018 onward remain closed. Products stay paused.

## Claims and authority

Forecast gain remains the default confirmatory claim, consistent with Barry's
D018 choice. A positive score moment at zero asks a different question: whether
a working conditional mark association points in the published direction.
It need not mean that a development-trained forecast improves. Both statistics
are studied here. This freeze does not approve replacing the primary claim or
opening data. Claude reviews the evidence before the next design decision.

No rolling correction excludes slow co-variation by construction. The ten-mark
and twenty-outcome corrections can leave aligned trends; specificity stresses
report this separately from predictive-null error rates. Mean individual oracle
KL under mixed signs is not a pooled positive effect.

## Prospective observational candidate, still requiring implementation checks

Retain the observed clock, X5 extraction and working onset-window assumptions
from R2b; neither physical-onset containment nor a proper interval score has
been proved without additional assumptions about reports and observation times.
Use per-star development standardization of log bright span and subtract its
previous ten usable marks, including development. Fewer than three preceding
marks or an unusable previous covered gap means no mark offset.

B0R is the new candidate: per-star development B0 plus a common-to-both-arms
location correction using the latest twenty issued forecasts whose complete
scoring labels are actually available. Latest means issuance order among
available labels, not arrival order. Development supplies the warm start.
For the future interval/survival likelihood this requires prefix label versions,
candidate confirmation and coverage recognition, not simply the final window's
upper endpoint. No final observational implementation is certified by this toy.
Fit a nonnegative pooled coefficient on guarded development predictors, with
development-count weights capped at 40% per star; freeze it for evaluation.
Use evaluation-count capped weights for the pooled evaluation estimand.

B0R's simplicity motivates this post-R2b amendment. B2's worse development
likelihood is a descriptive comparison, not a prespecified adequacy rejection
or unique evidence about physical mean reversion. Keep B1R, uncorrected B0 and
B2 as named sensitivities. Choosing a smaller observed gain does not make a
post-result choice independent of results. None replaces the recorded R2b result.

## What this simulation implements

`src/dnmem/r2d_simulation.py` generates sequential Gaussian **point log gaps**,
with per-star baseline level, previous gap and older-five-gap mean effects.
An observed mark proxies the latent direct-effect mark; settings add missingness,
delayed outcome labels, shared trends/states, correlated epoch effects and
star heterogeneity. Issue times follow the prior onset plus a fixed bright phase.
Labels become available at onset plus the declared reporting delay. Features
and recalibration consult only labels available at that issue. Missing prior
gaps are retained as missing slots; they are not joined over.

The point-model location correction is the mean raw-base residual among those
twenty labels (the Gaussian Newton step); it never refits evaluation outcomes.
Nuisance coefficients and transforms are learned once on available development
outcomes. Development reference predictions use that end-development fit
retrospectively, not operationally issued historical parameter versions.
The pooled mark offset is refitted to these guarded development predictors.
Fewer than three development contributors gives the exact base in both arms.

This is an independently constructed learning/availability stress model, **not**
X5 recovery, onset-window scoring, conditional-survival fitting, an archive
replay, or a calendar forecast-yield simulation. Six equal-count nominal epochs
per star are grouped three per half. They are an analogy for the proposed two
18-year clusters, not eighteen actual years. The generator does not add heavy
tails, wrong-star estimates, missed-event inference or endogenous observing.
Those limits prevent claiming a final observational error-rate guarantee.

## Fixed grid, seeds and resource envelope

`data/provenance/r2d_precision/design.json` fixes 35 cases, 2,000 trials each:

- Twelve core cases: 4/8 stars × 600/1,100/2,000 test forecasts × zero/positive
  direct effect, 100 development events per star.
- Four strict predictive-null controls: 4/8 stars, clean/persistent histories,
  an oracle base with true latent mean and innovation variance, no estimated
  level correction and no direct mark effect.
- Twelve joint stresses: 4/8 stars × zero/positive direct effect, under
  persistent states/small development/missing marks; imbalance/heterogeneity/
  history-correlated marks; or cross-star states/noisy marks/delayed labels.
- Six specificity cases at five stars and 1,100 forecasts: common trends,
  common slow state, joint regime shift, delayed-history proxy, oversized
  development effect, and balanced opposite-sign effects.
- One three-star case exposes small-cluster granularity.

The positive nominal .004 nats is the individual latent oracle signal before
mark noise, centering, learning and weighting. It is not the achieved gain of
the frozen candidate, nor a universal effect size. Report both.

Each seed is the first eight SHA256 bytes, big endian, of
`r2d-precision-v1-independent-validation|case|replicate`. No prior development
simulation seeds are reused. No trial is redrawn on failure. Full trial lines,
including failures, are retained locally; only small aggregate results enter Git.
Use at most four local M4 workers; unit smoke timing is about .005 seconds for
one five-star/1,100-event trial. No remote resource or archive is required.

## Statistics, targets and decision rules

For both gain and the zero-offset score moment, report CR1/t intervals/tests
under star-half and whole-star clustering. This is a simple declared candidate,
not CR2/Bell–McCaffrey inference or an efficient nuisance-orthogonalized score.
Whole-star sign flips of the raw score contributions are an additional
sensitivity, exhaustively enumerating all 2^S patterns. They require independent,
symmetric star scores; their performance under the generator is measured rather
than assumed. With 3/4 stars the minimum one-sided p is .125/.0625, so no
amount of forecasts can give a 5% rejection by this procedure.

**No method selection on this grid.** Report all predeclared procedures;
choosing/tuning a correction afterwards needs a separate validation study.
Do not label any implementation a general Kline–Santos bootstrap. Their
regularity/asymptotic results do not supply finite-few-star guarantees for this
adaptive score. CR2 similarly needs a justified working covariance and estimator.

For each trial, the generator knows the true conditional mean `m` and fitted
base `mu`, variance `v`, current centered mark `z`, and frozen shift `b*z`.
It records exact predictable gain `b*z*(m-mu)/v - (b*z)^2/(2*v)` and score
`z*(m-mu)/v`. These are **realized-path predictable averages**, not unconditional
population KL. Report coverage of that gain target both including exact-zero
offsets and conditional on a nonzero offset. Identity trials are not allowed
to disguise poor nonidentity coverage.

Strict oracle-null rejection rates are predictive-null error screens. Estimated
base/no-direct-effect and specificity cases may have genuine predictive gain
over an imperfect base and must not all be called false positives. Report
their predictable gain/score and the frequency of positive expected score with
negative expected fixed-rule gain. Any extrapolation from association power to
forecast-gain power is prohibited.

Each proportion receives a two-sided exact 95% binomial Monte Carlo interval.
Observed rate ≤5% is a screen, not certification of a true ≤5% error rate.
Coverage is compared with nominal 90%, with its exact uncertainty. A robust
80% power claim would require the Monte Carlo lower bound ≥80% across the
stated admitted positive-effect envelope **and** satisfactory null/coverage
screens. Cases violating independence and mixed-sign cases are explicit limits,
not quietly discarded. If no tested N qualifies, say that no universal N is
established; give only conditional cell-level precision. No automatic star-data
opening follows any outcome.

## Source basis and handoff

Independent invented-number proofs are in the R2d design review. Primary
method sources checked: Clark & West's
[2005 working paper](https://www.kansascityfed.org/documents/5368/pdf-RWP05-05.pdf),
Kline & Santos's [2011 author manuscript](https://eml.berkeley.edu/~pkline/papers/ScoreFinal_web.pdf),
Pustejovsky & Tipton's [2016 author manuscript](https://jepusto.com/files/Pustejovsky-Tipton-201601.pdf)
and [CR2 corrigendum](https://jepusto.com/posts/pusto-tipton-2018-theorem-2/).
These support methodological distinctions, not validation of our custom procedure.

After independent review: decide what evidence and primary claim a multi-star
study should target, then take a concrete G3a development-only access proposal
to Barry. G3b test access, SS Cyg 2018+ access, specialist contact and release
remain separate closed decisions. No data yield has been measured for new stars.
