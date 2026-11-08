# A10b: repaired ledger, conditional forecast models and synthetic controls

Codex, 8 November 2026, base `5476d00`. Development specification, **not the
A10 real-evaluation freeze**. No 1960+ observations or real duration–following-
gap association is part of this tranche. Retain A10a and its pilot as the
pre-review record. X4 stays unchanged at `352a09e`; magnitude 10 and C1/7 d
remain the accepted conditional retrospective extraction definition (D017).

## Confirmatory question

Barry chose **“Forecast gain confirmatory (recommended)”** in the current
chat on 8 November 2026. Keep held-out M3–M2 forecast gain confirmatory and the
duration coefficient secondary. The independently reproduced 32% versus 77%
power figures concern different nulls, not interchangeable tests of one claim.
A coefficient estimated using evaluation outcomes freezes the specification,
not a fitted coefficient. Do not open the reserved block or change this choice
in response to synthetic or development results.

## Review correction

Prefix causality prevents later-row leakage. It does not prove that waveform
errors only dilute forecast information: a shared end error enters duration
and landmark age with opposite signs, so a duration mark can correct the
baseline's age error even with constant true duration. An independent exact
six-state example yields 0.087208 nats of gain through that route. The A10a
complete-gap covariance approximation is not a bound on forecast gain.

Similarly, a zero **direct** duration effect does not imply zero incremental
information beyond a noisy timing-only state proxy. Structured controls may
show genuine proxy information. Separate physical memory, measured-baseline
forecast information, and measurement/coarsening artefacts. No-effect pilots
report estimates and Monte Carlo uncertainty rather than treating a failure
to reject zero as evidence of absence.

## Repaired ledger and evidence

`a10-prefix-v2` uses the same 400 d lookback and emission-matching rule as
A10a. Features use rows through `emitted_at` only. A uniform latency changes
issue/age, not the information set. Filter block membership by **issue** time;
the repeat flag retains the preceding emission even outside the requested
window. Missing/unestablished end anchors are explicitly marked.

Choose the candidate next onset relative to the original emission before
applying latency. If it is established before delayed issue, flag the forecast
overtaken instead of assigning a later onset. An onset bracket straddling issue
does not establish survival; exclude it commonly with an explicit reason,
retaining the ledger entry. Preserve full monitoring gaps that straddle issue;
their lengths do not restart at issue time. A resulting zero-exposure censor
is retained with log probability zero for every model.

The live interval ends at the first coverage loss, next issue, or block end.
Confirmed onset indices may be credited only once. These are observation-
defined scoring windows. Repeat/false alerts and informative observation effort
remain scientific limitations: common evidence is not a proof of ignorable
coarsening or valid physical-cycle survival.

Outcome extraction at cutoff T first discards rows after T, then runs X4.
Every row records conservative `computed_as_of = evidence_available_at = T`.
Training uses this newly computed prefix evidence, with unresolved outcomes
right-censored at T. Never take final retrospective outcomes and merely filter
their issue times. The present model schedule is **frozen fitting only**;
earliest operational resolution times and online updating are not implemented.

## Conditional statistical forecast models

Use lognormal forecast clocks, conditional on survival to the observed
landmark age. These are normalized statistical forecast distributions,
not an identified physical/missed-event/observation likelihood.

- M0: stationary full-gap clock.
- M1: M0 plus centered log duration.
- M2: timing clock with centered previous log gap, when C1-covered.
- M3: the same timing architecture plus duration.

Training centers/scales are fixed. Missing marks use the corresponding
baseline; a missing covered previous gap routes M2 to M0 and M3 to M1.
If the end anchor is unavailable, all four use the **same** issue-anchored R0
remaining-wait distribution. Every fallback and training-subset count is
reported. This is a first AR-gap benchmark; selecting a stronger timing-only
state architecture remains necessary before the real evaluation freeze.

For a known end e and age a = issue−e, interval/censor log scores are
`log P(lower−e < Q <= upper−e) − log S(a)` and
`log S(censor−e) − log S(a)`. SciPy's stable normal log-CDF and upper-tail
subtraction avoid flooring probabilities. Fit by two deterministic starts of
bounded L-BFGS-B, reporting failed fits and bound/convergence diagnostics.
Do not silently replace a failed fit with a successful simpler model.

The shared-end sensitivity uses five equally weighted pre-landmark end nodes
over `[end_lo,min(end_hi,issue)]`; each node jointly changes duration, age and
outcome offsets. Take the ratio of marginal numerator and survival mixtures,
not an average of conditional ratios with unupdated weights. Onset and previous
gap are held fixed: this uniform bracket distribution is a **partial measurement
sensitivity**, not a calibrated joint endpoint posterior or a guarantee that
the age-error route is removed.

A second mark design uses a 12 d type indicator plus log-duration centered
within type. It is diagnostic in the declared subset; the one-covariate
Gaussian power numbers cannot be transferred to its two coefficients.

## Independent concordance before production scores

Commit source/config/input identities first. Use a fresh namespace
`a10b-concordance|<full-freeze-hash>` for exactly 100 three-year synthetic
histories, both latencies 0/2 d. Eighty use v2, twenty the unqualified v4 stress
family; round-robin cases and era windows are fixed by the script. Short
histories test implementation; they are not 100 real-sized qualification
records. An independently authored reference shares only the frozen X4/visit
primitives, not candidate ledger/evidence code. Compare every feature and
evidence field exactly. Hash both outputs. No production model scores until
all 100 match, including both latency checks.

## Full-chain development pilot

`configs/a10b_controls.json` fixes 56 trials: eight v2 trials per independent
null, structured zero-direct-mark, gross-error, persistent-offset, adaptive-
effort and injected-effect case; four v4 trials each for null and alternative.
V4 is explicitly unqualified and diagnostic. No family is retuned here.

Each trial replays the 50 open-era source-pattern years for development,
followed by 58 evaluation-pattern years, on an explicitly artificial timeline.
Use integer JD translations to preserve night bins, and 30 d empty seams
between independently generated blocks; seam monitoring loss censors rather
than inventing adjacent cycles. Development is about 300 issued forecasts;
evaluation counts vary and are reported, without selecting completed blocks.
No actual reserved-era schedule or event counts are used.

Cases sharing a null process use common random streams for paired stress
comparisons; replicate IDs are independent. Persistent observer offsets are
held across the entire synthetic development/evaluation trial. Adaptive effort
thins whole days using only previously retained bright/faint evidence; shorter
completed bright runs reduce subsequent effort to 0.35, longer ones retain
1.0, and accepted bright activity restores full effort. This is a deliberately
unqualified causal stress policy, not a fitted human observing mechanism.

Fit and score prefix-point, prefix-uniform-end, retrospective-current-boundary,
and oracle-timing views on the **same** evidence/issuances. Retrospective
features are a knowingly leaky diagnostic. Oracle information is available
only for a unique true event completed by issue; other issuances stay and use
the common unknown-anchor fallback. Oracle previous gaps are exact within a
source block. Do not truth-filter the primary ledger or its score population.
Type/within-type marks run for the first four null/alternative replicates.
The same subset also fits prefix point/uniform-end models at two-day latency;
it reuses immutable emission-prefix features but recomputes issue-window
membership and as-of evidence at the delayed issue times.

Report paired M1−M0, M2−M0 and M3−M2 log probability gains, all exclusions,
censors, fallbacks, failed fits and parameter diagnostics. Each trial also
gets a three-year cluster interval, explicitly diagnostic rather than a
calibrated confirmatory test. Across trials use a t Monte Carlo interval on
block means and report the small replicate count. Eight/four trials cannot
establish final power, type-I error or absence of small artefacts.

Only after these results and independent reconciliation should a larger
operating-characteristic grid be designed. Do not call this pilot the A10
freeze, operational replay, model selection on real correlations, or a result
about the reserved star history.
