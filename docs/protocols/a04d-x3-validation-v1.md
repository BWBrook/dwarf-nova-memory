# A04d fresh validation of X3: proposed specification

Claude, 7 November 2026. Status: **proposed**. Codex reviews it, completes any
ambiguity in writing, and freezes it before a production run, as with A04c.
The evidence and reasoning are in the
[A04d memo](../audits/2026-11-07-a04d-observation-review-x3-repair.md).

## Candidate and references

- **Candidate:** X3, `src/dnmem/extract_x3.py`, `DEFINITION_VERSION =
  "a04d-x3-v1"`, at the commit that adds this file. It stays byte-identical
  through validation; every parameter is a module constant.
- **References:** X1 and X2, unchanged since `90e9661`, run on the same rows.
  They are context, not candidates.
- X3 was calibrated on Claude's training batch (base string
  `a04d-claude-training-20261107`, `scripts/a04d_train_x3.py`). The 0.99
  interval level is its only outcome-tuned parameter. The A04c screen seed
  (`2026110704`) was never used for development.

## Benchmark v2 (Codex implements; X3 source withheld from the generator author)

Each change answers a failed posterior predictive check of the A04c v1
benchmark against open-era light curves (`scripts/a04d_morphology_check.py`,
`data/simulations/a04d_morphology_check_20261107.json`).

1. **No knot at a tested threshold.** The light curve keeps the same slope on
   both sides of 9.5, 10.0 and 10.5. Crossings are solved numerically.
2. **Decline rate independent of duration.** The slope at the crossing is
   drawn from a distribution calibrated by Codex so that the check's end-slope
   quantiles match the real ones (real median 0.333 mag/d, IQR 0.293–0.391,
   Spearman with duration 0.04).
3. **Rise rates matched** to the real onset-slope quantiles (median 0.667
   mag/d, q10–q90 0.21–1.88), including a slow-rise class.
4. **Scatter at the threshold matched.** Inflate observer scatter so that the
   check's end residual SD matches the real distribution (median 0.222 mag;
   v1 gives 0.176). Add an arm with fixed per-observer offsets, SD 0.2 mag,
   that are not shrunk.
5. **Quiescent level** set to the real visual median, about 11.8 mag.
6. **Cadence.** Keep random-phase renewal as one decisive arm. Add a
   *state-matched* decisive arm: on each synthetic day the schedule (observers,
   times of night, limit slots) is borrowed from the nearest real day of the
   same outburst/quiescent state within ±15 d, so observing effort follows the
   synthetic star as it followed the real one.
7. **Benchmark acceptance before scoring.** Codex runs the morphology check on
   v2 and reports it with the result. The benchmark is accepted if its median
   end slope, median onset slope and median end residual SD each lie within
   15% of the real values, and the end-slope Spearman with duration lies
   within ±0.15. A benchmark that fails is revised before any extractor is
   scored, not after.
8. Marginal duration and gap distributions stay as in A04c, separately
   calibrated, with no real association computed. They remain
   extractor-conditioned; say so.

## Seeds, arms and replication

- Validation seed base: the string `a04d-validation|` followed by the full
  commit hash at which Codex freezes this protocol. The hash does not exist
  while X3 is being developed.
- Decisive cells: threshold 10.0, independent null, 1910–1929, 1930–1949 and
  1950–1959, in both the random-phase and the state-matched arms, at **400
  replicates** each. The 1950s null-bias cells in A04c were inconclusive at
  200.
- Diagnostics: the copula alternative (200 replicates), thresholds 9.5 and
  10.5, the 1900s, the unshrunk-offset arm, and the A04c v1 template
  (200 replicates, reported but not gating: its knot at 10.0 fails check 1).
  On training seeds X3 already fails v1's end coverage (84.5–86.3%); that
  result should be reproduced and reported, not hidden.
- Calibrate observer offsets and scatter from residuals at outburst
  brightness (8.5–10.5 mag) as well as in quiescence. Correlated error from a
  biased observer across nights is the main threat to X3's intervals, and
  its weakest training arm (91–93%).

## Criteria (each decisive cell; the Monte Carlo interval must clear the bound)

1. Effective coverage of at least 90% at each boundary, with all interior
   true events in the denominator, as in A04c.
2. Short-event completeness of at least 95% outside March–May.
3. Fewer than 0.2 false confirmed episodes per year.
4. Absolute null association bias below 0.02 under the chosen coverage rule
   (C1 at 7 d unless only C2 passes).
5. **New:** X3's operational confirmation time (`confirmed`) precedes the
   true end in under 2% of uniquely matched events. Report its lag and its
   missing rate.

D and Q for X3 use its point estimates (`onset_t`, `end_t`); X1 and X2 keep
interval midpoints. Coverage uses the intervals. The scorer reads these
fields when present.

Also report conditional coverage, interval widths, duration bias and RMSE,
eligible pair counts, the share of boundaries using the adjacency fallback,
and coverage by fallback status.

## Eligibility rules to apply in the association diagnostic

- A quiet interval that holds an unconfirmed (single-observer) bright episode
  is censored, not treated as quiet.
- A gap-split episode (an internal observing gap over 7 d) censors both
  adjacent intervals.

## Decision

Pass in every decisive cell freezes X3 for open-era extraction (A05) and for
the A10 forecasting pipeline. Fail or inconclusive results are retained. No
parameter changes after validation seeds are drawn; any later repair needs a
new specification, a new training batch and new seeds.
