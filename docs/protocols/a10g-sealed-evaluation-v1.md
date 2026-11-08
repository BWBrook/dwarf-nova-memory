# A10g: implementation freeze for the single 1960–2017 evaluation

Codex, 8 November 2026, reviewing proposed A10f at `31ddd21`. This amends
implementation and interpretation details before access. **No 1960–2017
archive request is authorized yet.** Barry must choose the timestamp route
and explicitly authorize this frozen scope. D018 stays held-out forecast gain.

## Fixed forecasts and primary test

Parameters remain byte-identical to
`data/fits/a10e_1910_1959/frozen_parameters.json`, SHA-256
`ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3`.
All 26 source identities in the A10d receipt remain unchanged. X4, threshold
10.0, C1/7 d coverage, prefix-v3, frozen centers/scales, fallback routing and
all six frozen variants are unchanged. There is no primary refitting or
parameter updating. Ancillary S1 fits cannot enter a frozen score.

Issue times are in [2436934.5,2458119.5), 1960-01-01 through 2017-12-31
under the presumed native convention. Delay 0 is primary and delay 2 is a
sensitivity. The statistic is the mean M3−M2 log-score gain over all
score-eligible issuances, literal fallback zeros included. Ambiguous-survival
exclusions remain the existing frozen rule. Consecutive 6×365.25 d clusters
are anchored at 2436934.5. The existing cluster-sandwich SE and t with
(nonempty clusters−1) df provide the one-sided 95% lower bound and two-sided
90% interval. The primary result confirms exactly when the lower bound >0.
There is only one confirmatory statistic. No alternative subset, era, variant
or interval width may replace it. Without at least two nonempty clusters the
result is not estimable, not a non-confirmation.

## Pre-request authority and acquisition

The future live command requires a tracked, committed
`coordination/evaluation_access.json` containing Barry's verbatim go-ahead,
`approved_by` Barry W. Brook, the exact source-freeze commit, this protocol's
SHA-256, the parameter SHA-256, start/stop JDs and timestamp choice (`git` or
`zenodo`). The latter also requires the deposited protocol DOI. The decision
and access ledger entry must be committed/pushed before any request. No
placeholder authorization file is supplied by this tranche. The live path
fails before transport or native opening without matching authority.

Use the established AUID 000-BCP-220 and VSX native XML/CSV `mtype=std` query.
Start with the half-day context window [2436934.0,2436934.5], then each calendar
year 1960–2017. Provider endpoints are inclusive and adjacent windows overlap.
The last request ends at `nextafter(2458119.5,-inf)`, strictly before the
reserved boundary; reject any returned row at or beyond 2458119.5. No 2018+
request is sent. Native JD strings and unknown metadata are preserved without
time conversion. The API contract is pinned; unrelated submission-format
time tags do not authorize a conversion of its JD column.

Write response bytes and their hash receipt before parsing; append the query,
retrieval time, terms URL and hash to the acquisition manifest before parsing.
A response at the 50,000-row cap is retained as a split parent, then its
interval is bisected until every retained leaf is below the cap. Do not guess
pagination semantics. Empty leaves require explicit Count=0. Reject malformed
rows, unsupported target/query provenance, nonfinite values, conflicting
obsIDs, quarantine paths and out-of-scope times. Deduplicate only identical
obsIDs across overlapping windows and pre-1960 context. Redirects are blocked.
Raw bytes and identities remain outside Git.

Reuse the receipt-verified existing pre-1960 stream for causal-emitter context;
feature lookbacks remain 400 d. Only exact `Vis.`/`V` rows enter extraction.
Modern non-visual/quality-rejected rows remain in native provenance. A
synthetic invariance test verifies filtering changes no prediction/evidence
field beyond unused raw-prefix counts/last-row metadata. A separate private
observer-ID map retains previous sorted oNNNN IDs and appends sorted new
identities; it is never applied to the forecasting inputs and never mutates
the original benchmark cache.

## Sealed execution and concordance

One command verifies the frozen source, parameters, authority, receipts,
inputs and native scope; constructs both candidate and independent-reference
ledgers/evidence at both delays; scores the frozen system; writes
`primary.json`; and only then runs secondary analyses. No person or agent
inspects evaluation rows, counts, plots or intermediate summaries before that
primary file is written. Private automated parsing/validation necessarily
reads the data. Stage times are retained; raw rows are not printed.

**Any candidate/reference ledger or evidence mismatch halts before scoring.**
The candidate does not become authoritative merely because it produced an
answer; no mismatch-based deletion can substitute for the target population.
This supersedes A10f's permissive mismatch/exclusion rule. Preserve the failed
run and report that access consumed the block. No primary confirmation is
claimed from a failed concordance or numerical audit.

A crash/contract failure is retained. Any later minimal repair must be
outcome-independent, independently reviewed and committed with the diff; the
rerun is labeled post-access repair and cannot restore untouched status.
A secondary fit/profile failure leaves the primary sealed and is reported as
failed, never silently retuned. The future live acquisition manifest is
append-only; source checks allow only that controlled generated change.

## Named secondary analyses

**S1: association.** Fit signed M2/current/lagged offsets on evaluation
outcomes alone using the staged estimator. Also fit a genuine simultaneous
two-coefficient current+lagged offset on joint-valid rows, holding that same
M2 fitted on all timing-eligible evaluation rows fixed. Use common-row mark
transforms for the joint fit, bounds [−5,5], deterministic starts [0,0],
[.1,.1], [−.1,−.1], and the existing lognormal landmark likelihood. Report
convergence, row populations, transforms and design rank. Constant terms are
fixed; rank-deficient joint designs do not get coefficient-specific intervals.
Evaluation-only diagnostic profiles reoptimize the other mark coefficient
while holding M2 fixed. The numerical policy is chosen by free-nuisance
dimension before access: one dimension uses bounded scalar minimization on
the full declared interval, explicitly checking both closed endpoints; two
or more dimensions use box-constrained L-BFGS-B with three-point numerical
gradients. Zero dimensions evaluate directly. The frozen implementation
records scalar xatol=1e-10, maxiter=1000; multidimensional relative step
cuberoot(machine epsilon), ftol=1e-12, gtol=1e-8, maxiter=1000 and maxls=50.
Recomputed objectives must agree within 1e-10×(1+absolute objective).
The solver interfaces follow the official SciPy
[`minimize_scalar`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize_scalar.html)
and [`minimize`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html) documentation. Every optimizer must report success with a finite,
in-bounds solution and a recomputed finite objective matching its reported
value; multidimensional gradients must be finite. Existing profile nesting,
likelihood-ratio and material-improvement checks remain mandatory. This is a
fixed numerical method, not a retry after failed optimizer status. It repairs
the secondary-only finite-difference failures retained from rehearsals `79b5eae`
and `bfb2bc6`; the original A10d sources, estimator and forecasts stay unchanged.
Conditional survival normalization does not justify a universal convexity
claim; any remaining fit/profile failure is reported without retuning.
All support intervals use LR cutoff 3.841 and are explicitly
conditional working-model support, not calibrated confidence or mechanism
identification. This is distinct from the old `joint_marks=True` pair of
separate one-offset fits. None of these fitted forecasts enters the primary.

**S2: state sensitivity.** Frozen P3 equals M2. Report M3−M2 on joint-valid
rows; interpret evaluation-only lagged/joint S1 fits as model-dependent
association diagnostics, not a state/memory decision rule.

**S3: robustness.** Score each of the six existing frozen variants with its
own parameters, plus the primary three-year-cluster sensitivity. The
joint-placebo variant uses its predeclared joint-valid population. No
mismatch-exclusion replacement is available.

**S4: eras.** Report primary gains for 1960–1992 and 1993–2017, each with
six-year clusters at its own start. This marks overlap with CM92's pooled
sample, not proof of prior ignorance or a new independent confirmatory test.

**S5: descriptive calibration.** For M0/M2/M3, obtain remaining-wait CDFs
from the frozen censored-score likelihood (survival conditioning once).
For interval onsets report [F(lower),F(upper)] and its midpoint decile. These
resolved-onset mid-CDF deciles are descriptive under outcome selection,
not a calibrated PIT-uniformity test.

For central 50% and 90% predictive intervals, classify each scored outcome:

- onset bracket fully inside predictive interval: definitely covered;
- onset bracket disjoint: definitely not covered;
- partial overlap: undetermined;
- right censoring at/above predictive upper endpoint: definitely not covered;
- other right censoring: undetermined.

Report all three counts and coverage bounds [covered/N,
(covered+undetermined)/N] over **all scored issuances**, including censored
ones; never turn censoring into noncoverage or delete it. Report M2−M0 gain,
and standardized q/L/x means/SDs on their relevant feature populations. Record
missing-L mean imputation separately: the training zero/one transformation
reference need not describe a selected evaluation subset.

**S6: inventory.** Report primary issued/scored/evidence/route counts by
fixed six-year block after writing the primary result.

## Interpretation

Sign confirmation and numerical magnitude comparison are orthogonal fields:

- A positive primary lower bound confirms incremental forecast information
  under this frozen visual extraction and measured baseline. It does not
  identify a physical mechanism.
- Otherwise the primary does not confirm. A wide interval is inconclusive;
  compatibility with zero and with a specified reference value must be read
  from the interval, not inferred from the sign of the point estimate.
- Separately report whether the upper endpoint is below the fixed numerical
  reference 0.004519560867443926 nats. This compares forecast gain with an
  A10d simulation mean (MC SE about .00137), not with a known physical effect
  or a universal equivalent of partial r=.13. It can occur alongside positive
  sign confirmation or alongside nonconfirmation. It is not a second primary
  test and cannot establish absence of a physical duration association.

Retain the finite-screen caveat, injected-effect joint-MC containment 85%,
modest scenario-specific power, observation-time rather than operational
availability, single-star scope and known CM92/development exposure. Pooled
3/220 confirmations and 5/220 development-LR exceedances are descriptive
case-arm counts with shared seeds; binomial intervals treating them as
independent are not valid. Median issue age alone does not prove negative
measurement coupling. The 8.12 conditional lag-zero frequency ratio is an
exploratory simulator comparison, not posterior odds or a model Bayes factor.

## Rehearsal, freeze and publication

Run the complete sealed command on a synthetic native-format surrogate with
namespace `a10f-rehearsal|<freeze full hash>`, including non-visual/flagged rows,
limits, metadata, overlapping boundaries and empty-response fixtures. Do not
use a desired sign/significance as a rehearsal acceptance condition. The
independent checker must reproduce every score and the primary interval;
all planned diagnostics must either complete or report a predeclared failure.
The source and parameter hashes must remain unchanged throughout.

Commit the implementation before this seeded rehearsal. Later audit/report
commits may add documentation and results but cannot change any source,
configuration, protocol or parameter byte bound to the freeze. A source repair
requires a new freeze/namespace and preserves the earlier attempt. Prepare a
protocol-only preregistration bundle, with no raw data or observer identities.
A Zenodo deposit, if Barry chooses it, provides an external timestamp before
project-time archive access; it does not establish universal outcome ignorance.
Until explicit later-data authority is committed, only rehearsal mode may run.
