# R1: observation-score, censoring and endpoint diagnostics

Codex, 9 November 2026. This amends the proposed A10n/D032 contract before
new diagnostic scores are inspected. It is a post-result research protocol,
not a new preregistration or confirmation. Independent contract review:
`docs/audits/2026-11-09-r1-observation-contract.md`.

## Scope and preservation

- Use only retained, already opened SS Cyg development/evaluation inputs
  through 2017, committed aggregates and the recorded synthetic generator.
- No archive request, new-star record or SS Cyg 2018+ observation, count or
  coverage summary may be accessed. New-star opening remains Barry's decision.
- Preserve the original run, source, parameters, evidence, scores and receipts.
  Do not rewrite the article, supplement, brief or agent guide during R1.
- New prospective outcome code is explicitly versioned separately from the
  frozen v3 builders. Its correction does not replace the original result.
- Four local workers are allowed for the defined synthetic grid on the M4
  mini. Target memory is under 3 GB; if observed memory exceeds 8 GB or a
  timed preparation predicts more than two hours, reconsider the resource.

## Amended observation contract (E1)

The frozen statistic is a paired **working interval log-score** difference
for the archive/extractor-defined outcome. The scientific latent target is
an idealised visual-magnitude-ten rising crossing associated with the next
outburst, not the physical initiation of a disc instability. Identifying it
with the next confirmed X4 episode additionally requires correct association,
no intervening missed/recurrent crossing and an appropriate risk set at issue.

Decisive reported estimates at least one magnitude from the threshold do
not prove error-free latent bright/faint states. Their visit aggregation,
measurement error and episode-selection convention remain assumptions.
X4's fitted intervals are not invariably nested inside the report clips:
`_clip` returns an envelope when intersection fails. Recompute and retain
the clip bounds separately, recording conflicts and missing bounds.

For history H and the selected risk set S, a sufficient ignorable set-score
contract would require the full observation kernel to factor as
K(Y|t,H,S) = c(Y,H,S) 1{t in A(Y)}, with observation parameters distinct from
forecast parameters. Restricting visit times alone does not establish this
condition for noisy reports, validation, confirmation, episode association,
report selection and stopping. Adaptive observing need not be clairvoyant to
violate the reduced scalar-onset contract. R1 does not establish this full
factorization.

X4's normalized crossing kernel is also not automatically a full measurement
likelihood. Its Gaussian change of variable gives an effective slope-prior
tilt by absolute slope. Data-dependent point selection, variance estimation
and clipping remain outside a proved generative observation model. Use it
as an **X4-kernel compatibility sensitivity**, not a certified likelihood.
Agreement of sensitivities within ten percent is a descriptive prediction,
not a validity gate or a proof of latent-onset propriety.

## R1a: censoring audit and prospective correction

Audit the builder's actual first eligible confirmed candidate for every one
of the six original censored issuances, including un-emitted episodes. Verify
retained hashes and reproduce both frozen builder outputs before drawing a
conclusion. Report occurrence counts, original contributions and whether the
prospective correction changes any of the 441 evidence records.

Preserve `prefix_features.py` and the frozen reference builder. Add an
explicit v4 working-set builder and a separately derived reference route.
For issue tau, stopping cutoff C and candidate set (L,U]:

- U <= tau: overtaken; L <= tau < U: ambiguous survival (unchanged exclusions).
- tau < L < C < U: right-censor at L, retain original C and cause as metadata.
- L = C < U: retain C. U <= C: retain the full interval.
- L >= C or no candidate: retain C.

These statements are conditional on the working-set interpretation; they do
not prove physical survival for an uncertain boundary set. Test exact ties,
coverage, supersession, record end, repeat emissions and ambiguous risk sets.
Dropping all six observations is a descriptive check, not a bound on all
possible observation-model changes.

## R1b: alternative real-data scores, with frozen calendar forecasts

Keep the fitted parameters, issuance times and predictor ledger fixed. Start
from the original 441-record population and original candidate association.
Evaluate the following, without refitting or choosing favourable cases:

1. **Decisive-report set:** probability assigned to the separately recovered
   (a,b] clip from the decisive faint/bright visit summaries.
2. **X4-kernel compatibility:** integrate the same conditional calendar-time
   forecast density against the exact frozen X4 Gaussian-mixture crossing
   kernel truncated/normalized on (a,b]. Do not silently substitute an
   adjacency kernel or claim that this is a proved observation likelihood.
3. **Point-extraction density:** conditional calendar density at saved
   `onset_t`, with point time as a declared approximation, not physical truth.

Use the prospective cutoff rule independently for each alternative set.
Re-establish relation to issue and stopping time; do not assert survival to
the middle of a straddling set. If an alternative complete set ends by C,
score it as an event even when the frozen label was censored; enumerate any
such promotions. Point = C counts as an event; point <= issue is unavailable.
Original no-candidate censoring remains a
working survival outcome. Missing/nonfinite/reversed clips, missing kernels,
overtaken or ambiguous alternatives are reported, never replaced with an
invented finite interval. An original identical-model fallback has exactly
zero paired contrast for any common observation treatment; retain and label
that identity rather than inventing an individual likelihood.

For each variant report its usable count, reasons for unavailability, routing,
mean paired gain, CR1 interval and rank association with the primary. If
availability differs, also recompute the original primary mean/interval on
the identical usable subset and report the paired change. Report the common
subset shared by all variants as well. Never present subset changes as an
improvement on the original confirmatory test. Use the original 2191.5-day
blocks anchored at JD 2436934.5 and the same Student-t rule.

Validate interval and point scores independently against the frozen scalar
score route. Check kernel integration with a second quadrature rule, explicit
support/tail checks and convergence; report numerical errors separately from
measurement assumptions. Preserve private per-issuance results outside Git;
publish aggregate diagnostics and hashes only.

## R1c: synthetic endpoint dose response and paired truth target (E2)

Use the A10d v2-phase **null and structured** cases, replicates 0 through 39,
with original base `a10c-oc|8f5df44b950ec5781ba1e31e074e56976909a051` and the
recorded block seeds. Retain complete synthetic truth, including partial
boundary events; do not join independently reset blocks across their seams.
Verify sigma-zero regeneration against retained primary records where present.

Use one independent standard normal z per *observed episode identity*, with
the fixed namespace `r1-endpoint-dose-v1`. Use the same z across sigma values
0, 1, 2, 4 and 6 days. Identity comes from observed bright-visit membership,
not truth or the following interval. Propagate the same end perturbation to
all prefix appearances: current duration/age, the next preceding gap, recent
gap history and lag duration. Preserve issue times and onset estimates.

Keep invalid perturbations visible: an estimated end after issue disables the
landmark and uses common R0; nonpositive duration disables the mark; invalid
previous gap disables timing under the established routing. No clipping,
redrawing or dose-dependent deletion is permitted. Count all affected routes.

Fix diagnostic anchors at sigma zero: unique truth-matched episodes, genuinely
completed and still quiescent at the original observed issue, first emission
per truth event. Do not select by later resolution or score. Keep those anchors
at every dose; enumerate false, unmatched, repeated and nonquiescent emissions.
Where cheap, also report the ordinary all-issued extracted-score comparison
to show the relation to the original 441-issuance estimand.

At each dose fit the ordinary measured-feature M2 and constrained duration
offset using synthetic development only and v4 working-set-corrected extracted
outcomes, then freeze. Separately fit/score a legacy-v3 sigma-zero comparator
per history; verify it against retained A10d records and report v4-minus-v3
changes and backoffs separately from the end-dose effects.
Score the **same calendar-time predictions** on the fixed anchors against:

- extracted working evidence;
- exact true next threshold onset, with administrative censoring at the first
  of next observed issue, coverage stopping, block end and period cutoff.

A true onset by the original administrative policy cutoff C is an event even
when v4 backs its extracted censor down to L. It is also an event when extraction missed it or its end lies
after C. Score truth events by exact density, not an arbitrary tiny interval.
Compare extracted and truth gains on their common scored anchors and report
any extracted-excluded anchors separately.

At sigma zero run a separately fitted/frozen **composite oracle** for both
cases, using true ends, durations and gap history and truth targets on the
same anchors. This is predeclared regardless of whether the measured route
is positive. It changes several measurement errors together; it cannot
attribute all differences specifically to current-end error.

Report history-level means and MC SEs (40 independent histories per case),
paired dose-minus-zero changes, route/anchor counts and failures. Plot the
curve against the original 0.01653 reference, but do not equate a crossing
with the real error magnitude: the anchor population and mechanism differ.

The A10n 0.004 / 0.0165 diagnostic thresholds may be shown descriptively.
Small gain at sigma <= 2 only limits this **added iid Gaussian end-error
mechanism in the fixed simulator**. It cannot rule out systematic/phase/state-
dependent real error, unseen waveforms, informative observing, missed events
or other observational pathways. Six days in a counterexample is not a lower
bound on what any measurement mechanism would need. Failure to reach the
reference by six days is not a certification of negligible real artefact.

An outside-grid preparation-only smoke uses replicate 999 and namespace
`r1-endpoint-dose-development-v1` to time extraction and validate identities;
it performs no dose fitting/scoring. Commit the full implementation/tests and
this protocol before running the 80-history score grid. No seed may be dropped
for an inconvenient result; preserve failures with their cause.

## R1d/e and handoff

Independently derive Figure 1's two median remaining waits and probabilities
within thirty days from frozen parameters/feature, and compare the saved CDF
grid interpolation. These are one date-selected forecast example, not average
accuracy or observing benefit. Add a provisional claim, without changing the
figure or draft yet.

Recompute the per-setting A10d table from retained history-level records and
compare committed aggregate values. Include confirmation uncertainty and
reference containment where available. Distinguish means, individual histories,
MC uncertainty and physical no-direct-effect scenarios. The real point estimate
may exceed every **scenario mean** without exceeding every simulated history.

Agree the R2 expansion direction: measurement validity, stronger evolving-state
baselines and star-by-star sealed tests belong in one design. Classification
and development-only screening, precision/cost planning and a concrete cohort
come before any new access request. No new-star or 2018+ opening, outside
contact, byline/venue decision or manuscript release is authorized by R1.
