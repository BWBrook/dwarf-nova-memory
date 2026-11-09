# R2b v1: frozen exploratory SS Cyg execution

Codex, 9 November 2026. Amends Claude's preserved `r2b-execution-v0.md`
(D038), after independent contract review. This protocol, configuration,
sources and tests are committed before the actual feature preparation or fits.
No result under R2b exists at this freeze.

## Scope and invariants

Use retained, already opened SS Cyg observations strictly before JD2458119.5.
Fit on issues from 1910-01-01 to 1960-01-01 (exclusive; JD2436934.5), with
all training evidence reconstructed from that prefix alone. Evaluate issues
1960-01-01 to 2018-01-01. No archive requests, other-star observations/counts,
SS Cyg 2018+ information, outside contact, manuscript release or product rewrite.
Original X4, A10 forecasting sources, parameters, outputs and protocols remain
unchanged. All R2b results are post-result exploration, never confirmation.

## 1. Causal clocks and histories

Accept the decisive-bright abort revision: choose the first decisive-faint
visit available after the original last threshold-bright report. Issue at the
later of its closure and the original emission. Abort only if a decisive-bright
visit (magnitude at most nine) becomes available after the original emission
and by the scheduled issue. Recount, without scores, before model execution;
330 development and 441 evaluation issues are expectations, not forced counts.
Keep abort/failure rows separately; never silently replace their anchor.

All DF feature visits must be closed by issue. Associate the current candidate
using raw peaks/observer counts, without fitted end or fitted confirmation.
Associate a past candidate to its own previously scheduled emission/DF anchor
uniquely using raw peak identity. Missing/ambiguous association makes that
consecutive history slot missing. Never join across it, skip a candidate or
substitute an X5 post-peak anchor. Own scheduled anchors remain immutable.

The window is 400 days with the existing thirty-day boundary margin. Rebuild
the state from the declared prefix once per issue; measured gaps and explicit
missing slots are the observations. DF history gaps end at the next candidate's
X5 lower onset support. This is a measured-history forecasting convention, not
known latent quiet intervals. Point clocks retain their X4 history convention.

Prepare P-orig (point at original issue), P-DF (observed clock at delayed issue),
and P-match (point at that same delayed issue). Fit each on its own development
features. P-DF and P-match must have identical issue IDs/times and outcomes.
Do not compare an original-issue mean with a delayed-issue mean as a retention
ratio. Keep common model fallback rows. Unsupported outcomes are not empirical
zero gains; exact forecast identities may be counted separately as algebraic
zero contrasts without inventing outcome evidence.

## 2. Target and observation assumptions

Retain the proposed latent target: after completion of the preceding qualifying
episode, the last rising magnitude-ten crossing before the first latent
decisive-bright excursion to magnitude nine. It remains distinct from physical
disc-instability onset. It avoids treating a shallow, nondecisive excursion
as a qualifying onset, but it does not itself prove containment.

Retain A0 association/completeness/risk set, A1 containment or genuine survival
through censoring, and the complete normalized CAR premise A2. Exact photometry
and absence of a missed excursion before L are insufficient under current visit
aggregation: a faint visit's median can hide an earlier bright raw report and
discard a decisive report inside its support. Raw-support expansion does not
prove that a faint witness preceded the first latent decisive excursion.
Sufficient additional conditions must establish this ordering/association.
No assertion that failure requires an error of at least one magnitude is made.

Use unchanged X5 report windows and eligibility flags. The primary population
uses eligible windows; a separately named sensitivity admits available flagged
windows. Missing windows, unconfirmed candidate obstacles, issue-straddles and
invalid risk sets are explicit unsupported statuses. Never skip them to credit
a later event. Describe the result as conditional on this observation policy;
selection of supported outcomes is not proof of an unbiased latent estimand.

## 3. Outcomes, censoring and scores

Build one candidate-ordered outcome ledger per clock/issue population. Choose
the first candidate peak after the original emission's last bright phase;
keep every unconfirmed or unsupported obstacle. No future candidate calibrates
a feature. Training extraction sees only the pre-1960 prefix, including visit
closure availability; evaluation extraction sees only the opened pre-2018 prefix.

The observation cutoff C is the earliest coverage loss (over seven days), next
issuance or period end. Preserve its reason. Coverage loss and supersession
are selected observation cutoffs, not independent administrative censoring.
The fixed-C functional below is conditional on this realized C and A0/A1.

Report separately:

1. Working interval probability (or v4 censor/backoff survival) contrast,
   conditioning each clock on survival to its own issue exactly once. A2 is
   required for the proper observed-report interpretation and is not established.
2. Deterministic sample means of fixed-C mixed density/survival inf/sup bounds,
   including straddles, with their actual supported population. These are not
   confidence limits and do not bound an unknown censored latent density score.
3. On point clocks, X4 point-density sensitivities and their distinct population.

An absent supported outcome remains absent in both arms. Numerical failure is
a run failure, not a zero gain. Preserve all failures and receipts. Pair H3
only on identical supported outcomes; report exclusions and algebraic identities.

## 4. Models, covariates and fitting

Keep R2a B0/B1/B2 forms, bounds, starts, discount grid, 400-day state rebuilding,
fallbacks and once-only survival conditioning. B0 is newly fitted on the strict
history, not the frozen original M2. B2 is a two-state windowed working filter.
No marked forecast updates the timing state.

Fit timing parameters on supported development outcomes. Save every multistart
attempt/objective, not only the winner. A base is stable only if every declared
start converges with finite free gradients, at least two succeed, and successful
objectives differ by at most 1e-6 times max(1, absolute best objective). Report
rank deficiencies and boundary values. Finite starts do not certify a global
optimum or identifiability. Preserve unstable B2 as an explicit diagnostic;
its sealed-test replacement rule is based on development stability, never gain.

Fit a centered/scaled log-duration offset constrained to [0,5], holding each
base's timing parameters, variance and routing fixed. Evaluate zero and five
alongside the scalar interior optimum. Zero beta/missing mark returns the exact
base. Only anchor+previous-gap-available rows may use a mark. Mark transforms
are learned on supported timing-available development rows alone.

Secondaries: replace duration by the positive observed-span threshold-excess
flux proxy, and by observer-night rate in that same causal bright span. Rate
counts closed visits (including limits), distinct observer-nights, divided by
span+one day. Its span depends on the light curve; it is an observing-intensity
sensitivity, not a mark known to be independent of physical duration. A positive
or nonpositive constrained rate result cannot identify or exclude all cadence
pathways.

DF-c: jointly refit the DF B2 timing base with standardized raw `c_end` as an
extra covariate, coefficient in [-3,3]; missing cadence uses the development
center (zero standardized value). Then add duration with all timing quantities
fixed. No evaluation covariate or outcome determines centers/choices.

### Local lag-sensitivity index, not a ceiling

Retain the proposed cadence summaries only as descriptive raw-report gaps,
available by issue. Their relation to latent phase durations is an additional
assumption. Compute v0's one-lag index J Delta-squared/2 with each fitted base,
absolute last-gap derivative, and the unconditional lognormal location Fisher
formula. Record unsupported cases rather than zeros. Label omitted older-history
effects (especially B2), survival conditioning, finite-shift remainder, latent
phase travel, morphology and selection.

This local quadratic approximation is not an upper bound. Conditional shifted
lognormals already violate it in an invented exact-model example; support
changes can give infinite KL. The data-processing inequality does not promote
the approximation to a bound. No comparison with H2 can rule cadence out.

## 5. Headline contrasts and uncertainty

Fixed before any score:

- H1: P-orig, B2+duration versus B2, working interval score.
- H2: P-DF, B2+duration versus B2, working interval score.
- H3: paired H2 gain minus P-match point-clock B2 duration gain.

All other rungs/marks/policies, bounds, point densities and local indices are
secondary or descriptive. Report the B2 development stability beside each H.
No favorable secondary replaces an unfavorable headline contrast.

Reference intervals: six-year CR1/t blocks starting JD2436934.5; companion
twelve-year blocks from the same origin. Use actual nonempty block count minus
one degrees of freedom, rather than inventing ten/five clusters if support is
lost. Report all block means, block lag-one ACF and issuance-ordered gain ACF
lags one through ten. Interval-midpoint log residual ICC/ACF diagnostics are
measurement/selection-conditioned proxies, with censored/unsupported cases
excluded; they do not identify the latent forecast-error process.

Say "positive under both blockings" only if both 90% lower limits exceed zero;
otherwise use "positive estimate, dependence-sensitive" or "uncertain" as
appropriate. None is confirmation or guaranteed coverage. Weak or negative DF
does not identify an artefact; B2 removing gain does not uniquely identify a
slow state. All interpretation remains conditional on the named measurements.

## 6. Future sealed design remains prospective

Fix DF, B2, X5 working interval score, pooled nonnegative mark offset and the
R2a normalized forty-percent star cap before R2b. B1 may replace B2 only on the
predeclared development stability failure above, not because it yields a gain.
An X5 likelihood claim still needs A2; the sealed statistic cannot fix it.

Drop star-by-six-year independence. Eighteen-year or whole-star clustering are
proposals requiring R2d review before any new archive opening. Plug-in simulation
at one estimated dependence setting and a 0.88 coverage cutoff are not proof
of 90% coverage; uncertainty in dependence and small star counts require a
declared stress envelope. Whole-star clustering also needs independent stars
and adequate cluster count. Do not call either procedure validated yet.

R2b can inform precision planning using the smaller of .010 and H2's estimate,
with uncertainty clearly stated; it cannot choose the sealed clock/model/score
by gains. G2 remains open. Barry's G3a development-only new-star opening and G3b
test opening are separate later decisions, as are SS Cyg 2018+ and any invitation.

## 7. Execution receipt and review

Commit source/configuration/tests first. Run a full synthetic raw-report
rehearsal and independent score checks, then gain-free actual feature recount.
After guards pass, execute development fitting, lock saved parameter hashes,
then score evaluation without retuning. Persist training/evaluation evidence,
models, per-issue results and run/failure receipts in ignored output; publish
only small aggregates and source hashes. New claims stay provisional for Claude.
Product texts/PDFs stay paused. Hand Claude the results, failures, conditional
assumptions and the still-unsettled R2d precision problem.
