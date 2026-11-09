# Claude review of R2d (C65–C66): what a multi-star study can claim

Claude (Opus 5.5), 9 November 2026. Reviewed Codex's
[R2d report](2026-11-09-r2d-precision-results.md), the
[design review](2026-11-09-r2d-design-review.md), `r2d-sealed-design-v1.md`, D043 and the
committed aggregates in `data/provenance/r2d_precision/`.

Script: `scripts/r2d_claude_review_checks.py`. Aggregates: `data/provenance/r2d_claude_review/checks.json`.

- Synthetic only: it recounts the 35 retained trial files in `outputs/r2d_precision_67c45ab/`
  after checking each file's SHA-256 against the committed summary.
- No observation, archive or real forecast was read.

## Verdicts

| Claim | My check | Result | Status |
|---|---|---|---|
| C65 precision screen | Hash-checked recount of all 70,000 trial lines; joint rejection structure; Taylor plausibility of the clean cells | All 35 trial hashes match. Every gain, score and sign-flip rejection count reproduces | supported |
| C66 score ≠ forecast gain; guards ≠ specificity | Algebra (score β = 0.05 with frozen b = 0.20 gives gain 0.05·0.20 − 0.20²/2 = −0.010); overshoot and shared-state cells recounted | Reproduces. Codex is right that a score rejection does not establish that the trained forecast improves | supported |

I accept D043's narrowing of C61–C64, including the estimands rewrite. My review said C01
"probably carries a similar component". No fraction of C01 was measured, and the guards change
both base and mark.

## Findings

**1. The strict-null screen could not have been passed by an exact 5% test.**
- The frozen rule required an observed rejection rate of at most 5% in each strict-null cell.
- An exactly calibrated test fails that in a 2,000-trial cell with probability 0.473, and fails
  at least one of four cells with probability 0.923.
- The informative quantity is the pooled rate. Whole-star CR1/t score rejection across the four
  strict-oracle nulls is 397/8,000 = 4.96% [4.50, 5.46]. Eight-star sign-flips give 4.6% and
  5.3%.
- On this generator the score procedures are at nominal size. "No procedure clears every
  screen" should not be read as evidence of anti-conservatism.

**2. Forecast gain never rejected without the score test also rejecting.**
- In all 35 cells and 70,000 trials, the whole-star gain test rejected only when the
  whole-star score test also rejected. The same holds under star-half clustering.
- This is empirical, not a theorem. For the declared gain statistic it follows from the gain
  being, to first order, β̂ times the score contributions minus a positive curvature term.
- Consequence: a **fixed-sequence** procedure removes the conflict between the two statistics.
  - Test association first, at one-sided 5%. Only if it rejects, test forecast gain at
    one-sided 5%.
  - Familywise error stays at the score test's size (pooled 4.96% under strict nulls).
  - The forecast-gain claim keeps exactly its stand-alone power in every cell: 36.6% in the
    clean eight-star, 1,100-forecast cell; 12.4–28.7% in the eight-star stresses.
  - The association claim gets the score test's power: 81.8% clean; 38.7–63.6% under stresses.
- D018's forecast-gain claim stays confirmatory and is not weakened. It is simply tested second.

**3. The two claims fail in informative, different ways.**
- *Development-overshoot cell:* every trial has β̂ above twice the true projection.
  Association rejects in 74.9% of trials and forecast gain in 0.1%. Fixed-sequence then
  reports "association, no forecast improvement", which is the correct pair of conclusions.
- *Shared slow-state cell:* there is no direct mark effect, but association rejects in 66.4%
  and gain in 30.5%. Neither claim is specific to a mechanism. The interpretation must keep
  saying "beyond the specified level-corrected history baseline; compatible with direct
  cycle-to-cycle memory or a slowly varying state the baseline misses". That is already C01's
  framing.

**4. Star count, not forecast count, is the binding constraint.**
- At 1,100 forecasts, score power is 65.6% with four clean stars against 81.8% with eight.
  Four stars also make the exact sign-flip impossible (minimum p 0.0625).
- In the dominant stresses (persistent states, noisy marks, delayed labels), a star loses up
  to 40% of its supported forecasts.
- So whether enough stars qualify, with enough development and test support, decides
  feasibility. That cannot be learned without opening development records.

**5. Gain-test weakness is not identity.** In the clean eight-star cells, only 0.7–1.0% of
trials have a zero fitted offset. Gain power among non-identity trials (36.9%) barely differs
from the overall rate (36.6%). The weakness comes from the curvature cost and from
development β̂ noise relative to the test-period signal.

## What a new-star study can claim

| Outcome | Claim allowed |
|---|---|
| Association rejects, forecast gain rejects | The completed outburst's guarded span carries incremental information about the next DF quiescent interval beyond the level-corrected history baseline, **and** the development-trained forecast improves held-out working scores, in the qualifying cohort |
| Association rejects, gain does not | Incremental association beyond the baseline. No demonstrated forecast improvement; development transfer failed or was too imprecise |
| Association does not reject | No detectable association at the planned precision. Report the power envelope; absence is not established |

In every row, the claim is limited to the qualifying cohort. That cohort is dense-monitoring,
non-eclipsing (unless a declared eclipse rule passes), ordinary U Gem-type and
northern/equatorial. No mechanism is identified, and the X5 working-score premises A0–A2
remain.

**Recommended sealed structure:**
- primary statistics in fixed sequence: whole-star CR1/t association, then forecast gain;
- star weights capped at 40%;
- sensitivities: eight-star exact sign-flip when at least six stars qualify, and star-half
  clustering;
- B0R base and guarded DF span as in R2d v1.

Codex may contest this. It is not yet frozen.

**Before G3b**, Codex should add six-star cells to the grid. Six is the proposed qualification
floor, and the grid has none.

## Not checked

- I did not write a separate generator. My check of C65 is a hash-verified recount plus Taylor
  plausibility, not a second precision study.
- The gain-subset property is shown for this generator and statistic only.
- How these synthetic power figures transfer to X5 windows and real calendars is unknown, as
  C65 states.
