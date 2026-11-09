# R2 v1: measurement assumptions, observed clocks and evolving timing baselines

Codex, 9 November 2026, amending Claude's preserved `r2-design-v0.md` under
D035. This is an exploratory **preparation freeze**, not a new confirmation.
The independent review is `docs/audits/2026-11-09-r2-design-review.md`.

## Authority and stages

This turn completes R2a (implementation, synthetic checks and gain-free SS Cyg
preparation) and R2c (catalogue/literature screening and synthetic precision
planning). It does **not** fit or score new real-data R2b models. Before R2b,
Claude reviews the prepared implementation, diagnostics and interpretation;
its execution sources/parameters and population rules receive their own freeze.

Only retained, already opened SS Cyg inputs strictly before JD2458119.5 may be
read. No archive request, other-star observation/count/coverage query, SS Cyg
2018+ access, outside contact or paper release is authorized. New-star metadata
come from identified catalogues/literature, with source dates and ambiguity
recorded. The future multi-star opening remains Barry's G3 decision. Manuscript
products remain paused. Frozen X4, original forecasting sources, parameters,
receipts and scores stay unchanged; new implementation is versioned separately.

## 1. Targets and assumptions

The desired scientific target is a latent rising visual-magnitude threshold
crossing associated with a qualifying outburst; it is distinct from physical
disc-instability onset. A first reported bright state is another legitimate
observable target with different scientific scope, not intrinsically an invalid
forecast target. Choosing latent onset commits this study to measurement and
association assumptions.

Separate three premises:

- **A0:** intended episode association, no missed earlier qualifying onset,
  a stated recrossing convention, genuine completion and survival to issue.
- **A1:** conditional containment T in the declared (L,U], or the declared
  no-event-to-cutoff statement for a censor. This is an assumption, not a
  consequence proved by a one-magnitude report margin.
- **A2:** a full ignorable observation kernel, including report/limit values,
  visit aggregation, selection, confirmation, association and stopping. A
  sufficient CAR form is K(Y|t,H,S)=c(Y,H,S)1{t in A(Y)}, normalized over Y,
  with observation parameters distinct from forecast parameters.

The CAR theorem in v0 is valid under that full factorization. A claim that
observers cannot time an unreported onset does not establish the factorization.
Nondecisive reports, unretained checks, cross-band alerts, morphology and report
selection can matter. Recrossings/missed episodes and aggregation can defeat A1
with exact photometry. Contradiction rates and visit-rate comparisons cannot
certify A0–A2 or be converted to expected failed-bracket counts without a
calibrated observation model.

### X5 report windows

Retain every unchanged X4 candidate in peak order, including unconfirmed
neighbours. Copy fitted X4 points without replacing them. Separately choose:
first decisive-faint visit after the preceding peak; first decisive-bright visit
after that quiescence visit and no later than the current peak; last decisive-
faint visit before that bright visit. No decisive bright visit means unsupported
faint peak/no-U; never substitute the peak after inspecting scores.

Observer visits retain the frozen median-positive rule. Only all-limit visits
use their strongest numerical magnitude lower bound. A limit is not an exact
positive estimate. SS Cyg uses magnitude ten and margin one.

Median time and magnitude need not describe a real instantaneous state. Retain
representative bounds for comparison, but report L as the selected faint visit's
**first raw time**, U as the bright visit's **last raw time**. Preserve full
support and visit availability (first raw time+0.15 day). Missing, contested,
touching/overlapping supports, and decisive-faint recrossing before peak have
explicit flags; finite windows stay visible with separate eligibility. The
first post-peak decisive-faint visit defines the end clock; the preceding last
decisive-bright visit defines its lower end support. A following outburst's
brightening must not move this endpoint. Later-bright counts are descriptive.

### Scores and deterministic bounds

All distributions are calendar-time forecasts conditioned once on survival to
issue. Let h(t)=log g_D(t)−log g_B(t), and s(C)=log S_D(C)−log S_B(C).

- For a genuinely contained resolved event, inf/sup h on (L,U] bounds its
  realized point-density gain without CAR. Use endpoint limits, not a minimum
  presumed attained at the open lower endpoint. Common-origin lognormal pairs
  have quadratic h in log wait; inspect both endpoints and any interior vertex.
- A survival contrast at C is **not** the unknown latent point-density gain
  beyond C. An unconditional latent-point tail bound may be unbounded.
- For a fixed administrative C, bound the **mixed event-density/survival
  functional**: U<=C gives inf/sup h on (L,U]; L>=C gives exact s(C);
  L<C<U gives the min/max over h on (L,C] **and** s(C). This assumes A0/A1
  and genuine no-event survival for any no-candidate censor.
- Separately retain the working interval compatibility policy: U<=C scores
  interval mass; a straddle discards later event information and backs working
  censoring to L; L>=C/no candidate censors at C. Missing or issue-straddling
  windows are unsupported, not invented. This policy and the fixed-C mixed
  bounds are different objects and must not be conflated.

Full A2 would license a proper observed-report score, generally not strict for
latent distributions. These preparations do not establish A2. Deterministic
sample bounds require no cluster model; approximate CR1 confidence limits do.
Ten SS Cyg six-year clusters are not an automatic conservative-coverage theorem.
No R2 result is to be labelled “E1 closed” solely from a positive interval or
lower-bound statistic.

## 2. Gain-free real diagnostics

After committed protocol/module/test hashes agree, use the receipt-verified
retained rows/visits/candidates. Report available and eligible windows, reasons,
widths and decade distributions, including limits. Count opposite decisive
cross-observer visits within 0.5 day with explicit denominators and descriptive
plateau/quiescence strata more than three days from selected edges. Report
faint-after-bright flags separately. No inferred physical error probability.

Report visit rates both strictly inside and including the selected (L,U] versus
the preceding five days. A selected last-faint/first-bright gap can have no
interior inspections even under homogeneous Poisson observing. These are
selection-conditioned summaries, not a test proving alerts or CAR.

## 3. DF: observed-clock sensitivity, not mechanism identification

The literal interpolated end estimate is removed from DF predictors. Exact
observed timestamps still depend on cadence. A pre-data counterexample with
constant true duration and cadence-dependent faint-report lag yields a positive
DF gain without any estimated end or photometric error. Therefore neither a
positive DF result nor a fixed retention ratio rules out observation/landmark
artefacts; a nonpositive result does not make such artefacts the leading cause.

First decisive-faint visits can arrive after the old 0.5-mag confirmation issue.
Do not use a future anchor. For each unchanged causal confirmation, select the
first decisive-F visit becoming available strictly after its last-bright closed
visit. Proposed DF issue=max(original emission, selected F availability), with
anchor at that F visit's last raw time. Abort a pending DF emission if a
threshold-bright closed visit arrives after the original emission and by that
proposed issue. This is a new causal policy; its population/latency may differ.

Associate a unique raw candidate peak in the original causal bright range
[bright_first_at−0.15,last_bright_at]. DF event eligibility uses at least two
raw bright observers, avoiding X4's fitted-end-dependent single-observer check.
Do not consult interpolated end values for this association or policy. The
positive bright-span mark is last minus first decisive-bright representative
time inside that causal range, available by issue. It can share reports with
outcome edges and other observational information. Test invariance to poisoning
all interpolated end fields and to adding arbitrary later data.

Prepare point-clock features at original issues and at matched later DF issues;
comparisons across clocks require the matched issue/outcome population. Do not
compare raw ratios to C01's 441-issuance mean as a mechanism test. A fluence
proxy may be prepared as trapezoidal threshold-relative optical excess flux on
the report-defined bright span with explicit gaps, never called bolometric
energy or a disc-mass measurement. No theorem requires it to outperform duration.

## 4. Concrete timing-model preparation

All rungs receive the same prefix-only 400-day report-candidate gap history;
past candidate onsets must be after prefix_start+30 days, with complete required
endpoints. Do not join gaps across missing/unconfirmed candidates: retain None
placeholders. Each history value is as reconstructed at the current issue and
has an availability timestamp <=issue. Rebuild the working filter from this
prefix; do not pretend revised older point estimates were available earlier.
This is a **windowed** filter, not full-history smoothing or missed-event inference.

Point-clock histories use X4 fitted points. DF histories use current lower
onset-report support minus the preceding decisive-F last-raw clock and seven-day
coverage. Keep frozen feature fields separately for reference. R2 B0 has the
timing **form** of M2 but is newly fitted with this stricter common history;
it is not the byte-identical original M2 comparator.

- **B0:** intercept, standardized previous log gap and standardized mean older
  log gaps. Missing older mean uses its development centre.
- **B1:** intercept, two standardized lag log gaps and an exponentially weighted
  older-gap level. Profile lambda over {0,.25,.5,.75,.9,.98} on development only;
  missing older values have zero weight, retaining their age positions. Missing
  second lag uses its development centre. Same previous-gap routing as B0.
- **B2:** state (x,u), transition diag(1,phi), process covariance diag(s_level²,
  s_ar²), observation log q=x+u with zero additional observation noise. This
  treats measured gap history as working observations, not noise-free physics.
  Missing entries advance prediction without updating. Initial mean (mu,0),
  covariance diag(1,s_ar²/(1−phi²)); phi in [−.95,.95], s_level in [1e−4,1],
  s_ar in [.03,2]. Propagate full predictive state variance. No duration enters
  filter updates. This is a filter-derived conditional forecasting rule.

Fit timing parameters by the declared conditional interval/survival working
likelihood on development only, using bounded multistart optimization and
explicit failure reporting. Regression coefficients in [−3,3], intercept/mu
in [−5,8], residual SD in [.03,2]. Use a common issue-clock R0 when anchor is
unavailable and common constant anchor-clock when previous gap is unavailable.

Fit one nonnegative standardized log-mark offset per rung with its timing
parameters/predictive variances held fixed. The mark centre/scale are identical
across rungs within a clock and derived only from development. Require covered
previous gap for a mark; missing/nonpositive mark returns the base exactly.
Beta=0 must return the identical base distribution, including fallback routing.
Training/evidence availability and serialization are checked explicitly.

R2a synthetic model checks use namespace `r2a-model-controls-v1`, three seeds
per stationary-AR, drifting-level and direct-duration process, 120 development
and 120 later forecasts. Mean gap is about forty days, residual log SD .35,
AR coefficient .4, duration shift .10 per standardized log mark in the direct
case; drifting level is an AR(.995) perturbation with innovation SD .03.
Report finite control outcomes without claiming calibrated error rates. Test
Gaussian conditioning against a joint multivariate-normal calculation, missing
update uncertainty, zero nesting, future leakage, fixed-baseline offsets,
optimizer failure and unsupported score cases. No synthetic control is tuned
against real R2b gains. Freeze its implementation before running the batch.

## 5. R2c cohort and precision preparation

Use identified catalogue versions and primary literature, recording URLs,
source dates, fields/passbands, hashes and unresolved classifications. Retain
all screened exclusions and published-analysis exposure years. Eclipse flags
and SU/Z Cam ambiguity cannot be waved through as ordinary outbursters.
Catalogue minima may be mideclipse; require a non-eclipse visual range for
proposed thresholds. A named catalogue/rounding rule is necessary for any
midpoint constant; different passbands/range conventions are not interchangeable.

The proposed future split is development before 1990-01-01 (JD2447892.5), test
1990-01-01 to 2026-01-01 (JD2461041.5), **36 years**. This is not authorization
to request any rows. Catalogue-only constants, extraction qualification,
exposure/eligibility and a concrete cohort need review before G3. No test data
may guide dropping a star. A forty-percent star-weight cap needs at least
three qualified stars; normalized weights are min(.4,k*n_s), with k chosen
so weights sum to one. Star-balanced results remain distinct secondaries.

The original SE times sqrt(441) is an effective uncertainty scale, not a known
iid per-forecast SD. The 400/1100/1700 counts are conditional fixed-variance
normal approximations, not measured multi-star power. Freeze the exact
`data/provenance/r2c_catalogue_power/power-design.json` and runner/tests before
its thirty-five-scenario, 2,000-replicate score-level study. Known and fitted
positive pooled offsets use the same evaluation draws; the fitted rule learns
per-star intercepts/offset on independent synthetic development. Report achieved
gain, confirmation uncertainty, overall/interior coverage and exact-zero identity
fractions. The grid varies N, effect, training size, star count, reliability,
heterogeneity, weight imbalance and explicit within/serial-block dependence.

This planning simulation does not implement photometry/X5 extraction, missing
events, censoring, state-filter learning or estimated predictive variance. It
cannot certify a universal 5% error rate or assert a qualified forecast count.
Future primary comparator and uncertainty method stay proposals until these
results and the SS Cyg ladder are reviewed; dependence across a star's six-year
blocks must be examined rather than presumed absent.

## 6. Interpretation and handoff

Keep the original C01 working result and all failed specifications. Real R2b
scores will be exploratory, conditional on named A0/A1/A2 premises. A positive
window score or positive DF statistic cannot identify physical memory, close
the measurement problem, or prove CAR. Stronger-baseline comparisons quantify
incremental information over those measured-history rules; loss of gain does
not uniquely identify a slow state. Prefer absolute paired differences with
uncertainty over unstable retention ratios.

R2a/c finish when implementations, gain-free SS diagnostics, catalogue/exposure
ledger and explicitly limited precision study are reproducible and independently
checked. Then Claude reviews, fixes any scientific choices and freezes the R2b
execution before scores. Barry's eventual G3 request must name the actual cohort,
split, target, assumptions, qualification/dropout rules, primary weights,
dependence method, achievable precision and remaining limitations. No new
authorization question is needed during this preparation.
